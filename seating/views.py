from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from .models import ExamSchedule
from .utils import generate_seating_allocation

# ---- Added home view ----
def home(request):
    return HttpResponse("<h2>Welcome to the Virtual Seating Arrangement System</h2>")


def generate_seating_view(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)
    message = generate_seating_allocation(schedule)
    return HttpResponse(message)


def preview_seating_view(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)
    allocations = schedule.seatallocation_set.select_related(
        "student", "classroom"
    ).order_by("classroom__room_number", "bench_number", "position")

    return render(
        request,
        "preview_seating.html",
        {"schedule": schedule, "allocations": allocations}
    )


from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from .models import SeatAllocation

def send_emails_view(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, pk=schedule_id)
    allocations = SeatAllocation.objects.filter(exam_schedule=schedule, emailed=False).select_related('student', 'classroom')

    if not allocations.exists():
        return HttpResponse("No new allocations to send.")

    connection = get_connection()
    emails_sent = []

    for allocation in allocations:
        student = allocation.student
        
        subject = f"Exam Seating: {allocation.exam_schedule.subject.subject_name}"
        message = (
            f"Hello {student.name},\n\n"
            f"USN: {student.usn}\n"
            f"Room: {allocation.classroom.room_number}\n"
            f"Bench Number: {allocation.bench_number}\n"
            f"Position: {allocation.position}\n\n"
            f"Good luck!"
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[student.email],
            connection=connection
        )

        try:
            email.send()
            allocation.emailed = True
            allocation.save(update_fields=["emailed"])
            emails_sent.append(student.email)
        except Exception as e:
            emails_sent.append(f"FAILED: {student.email} ({e})")

    return HttpResponse("<br>".join(emails_sent))
