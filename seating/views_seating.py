from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect
from collections import defaultdict

from .models import ExamSchedule, SeatAllocation, Classroom, Student


# ---------------------------
# BACKEND LOGIC (already yours)
# ---------------------------
def generate_seating(request, schedule_id):

    schedule = ExamSchedule.objects.select_related(
        "exam_day", "subject", "subject__semester"
    ).get(id=schedule_id)

    exam_day = schedule.exam_day
    semester = schedule.subject.semester

    students = list(
        Student.objects.filter(semester=semester).order_by("usn")
    )

    parallel_schedules = ExamSchedule.objects.filter(
        exam_day=exam_day,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
    ).exclude(id=schedule.id)

    classrooms = Classroom.objects.all().order_by("room_number")

    SeatAllocation.objects.filter(exam_schedule=schedule).delete()

    created = 0
    student_index = 0

    with transaction.atomic():
        for room in classrooms:
            for bench in range(1, room.benches + 1):

                if student_index >= len(students):
                    break

                if not parallel_schedules.exists():
                    seat_side = "S"
                else:
                    other_schedule = parallel_schedules.first()
                    other_sem = other_schedule.subject.semester.number
                    my_sem = semester.number
                    seat_side = "L" if my_sem < other_sem else "R"

                SeatAllocation.objects.create(
                    student=students[student_index],
                    exam_schedule=schedule,
                    classroom=room,
                    bench_number=bench,
                    seat_side=seat_side,
                )

                student_index += 1
                created += 1

    return redirect("seating:preview_seating", schedule_id=schedule.id)



# ---------------------------
# FRONTEND TEST PAGE
# ---------------------------
def frontend_test(request):
    return render(request, "seating/preview_seating.html")


# ---------------------------
# REAL FRONTEND PAGE
# ---------------------------
def preview_seating(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    allocations = SeatAllocation.objects.filter(
        exam_schedule=schedule
    ).select_related("student", "classroom")

    total_count = allocations.count()
    emailed_count = allocations.filter(emailed=True).count()

    all_emailed = (total_count > 0) and (total_count == emailed_count)

    return render(
        request,
        "seating/preview_seating.html",
        {
            "schedule": schedule,
            "allocations": allocations,
            "all_emailed": all_emailed,
        }
    )



# ---------------------------
# TEMP EMAIL PLACEHOLDER
# ---------------------------
def send_emails(request, schedule_id):
    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    allocations = SeatAllocation.objects.filter(
        exam_schedule=schedule,
        emailed=False
    )

    count = allocations.count()

    for alloc in allocations:
        alloc.emailed = True
        alloc.save()

    messages.success(
        request,
        f"Emails sent successfully to {count} students."
    )

    return redirect("seating:preview_seating", schedule_id=schedule.id)

def home(request):
    schedules = ExamSchedule.objects.all()
    return render(
        request,
        "seating/home.html",
        {"schedules": schedules}
    )


def virtual_classroom(request, schedule_id):
    allocations = SeatAllocation.objects.filter(
        exam_schedule_id=schedule_id
    ).select_related("student").order_by("bench_number")

    benches = defaultdict(dict)

    for seat in allocations:
        if seat.position == "LEFT":
            benches[seat.bench_number]["left_student"] = seat.student
        else:
            benches[seat.bench_number]["right_student"] = seat.student

    return render(
        request,
        "seating/virtual_classroom.html",
        {"benches": benches.values()}
    )

def classroom_layout_view(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    allocations = SeatAllocation.objects.filter(
        classroom=classroom
    ).select_related("student").order_by("bench_number", "seat_side")

    benches = defaultdict(dict)

    for seat in allocations:
        if seat.seat_side == "L":
            benches[seat.bench_number]["left"] = seat.student
        elif seat.seat_side == "R":
            benches[seat.bench_number]["right"] = seat.student
        elif seat.seat_side == "S":
            benches[seat.bench_number]["left"] = seat.student

    return render(
        request,
        "seating/classroom_layout.html",
        {
            "classroom": classroom,
            "benches": benches,
        }
    )

