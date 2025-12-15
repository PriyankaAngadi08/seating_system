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
    )
    return render(request, "seating/preview_seating.html", {
        "allocations": allocations
    })

from collections import defaultdict
from django.shortcuts import render

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
           f"Seat Side: {allocation.get_seat_side_display()}\n\n"
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


from collections import defaultdict
from .models import SeatAllocation

def virtual_classroom(request, schedule_id):
    allocations = SeatAllocation.objects.filter(
        exam_schedule_id=schedule_id
    ).select_related("student").order_by("bench_number", "seat_side")

    benches = defaultdict(dict)

    for seat in allocations:
        if seat.seat_side == 'L':
            benches[seat.bench_number]["left_student"] = seat.student
        elif seat.seat_side == 'R':
            benches[seat.bench_number]["right_student"] = seat.student
        elif seat.seat_side == 'S':
            # single student → put on left side
            benches[seat.bench_number]["left_student"] = seat.student

    return render(
        request,
        "seating/virtual_classroom.html",
        {"benches": benches.values()}
    )

from django.shortcuts import render, get_object_or_404
from .models import Classroom, SeatAllocation

from collections import defaultdict

def classroom_layout_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    allocations = SeatAllocation.objects.filter(
        classroom=classroom
    ).select_related("student").order_by("bench_number", "seat_side")

    benches = defaultdict(dict)

    for seat in allocations:
        if seat.seat_side == 'L':
            benches[seat.bench_number]["left"] = seat.student
        elif seat.seat_side == 'R':
            benches[seat.bench_number]["right"] = seat.student
        elif seat.seat_side == 'S':
            benches[seat.bench_number]["left"] = seat.student

    return render(
        request,
        "seating/classroom_layout.html",
        {
            "classroom": classroom,
            "benches": benches
        }
    )

