# seating/views_seating.py

from django.http import JsonResponse
from seating.models import (
    Student, ExamSchedule, Classroom, SeatAllocation
)
from django.db import transaction


def generate_seating(request, schedule_id):

    try:
        schedule = ExamSchedule.objects.get(id=schedule_id)
    except ExamSchedule.DoesNotExist:
        return JsonResponse({"error": "Schedule not found"}, status=404)

    exam_day = schedule.exam_day
    semester = schedule.subject.semester

    # FETCH ALL STUDENTS WHO HAVE THIS SUBJECT (current semester)
    students = list(Student.objects.filter(semester=semester).order_by("usn"))

    # Check if any other semester has exam at SAME TIME
    same_time_schedules = ExamSchedule.objects.filter(
        exam_day=exam_day,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    )

    mixed_semesters = list(
        same_time_schedules.values_list("subject__semester__number", flat=True)
    )

    # Example: [3, 5] -> mix, [7] -> single
    mixed_semesters = sorted(list(set(mixed_semesters)))

    classrooms = list(Classroom.objects.order_by("room_number"))

    # Clear previous allocations for this schedule
    SeatAllocation.objects.filter(schedule=schedule).delete()

    bench_counter = 1

    @transaction.atomic
    def allocate_single_sem(single_students):
        nonlocal bench_counter

        for student in single_students:
            for room in classrooms:
                if bench_counter <= room.num_benches:
                    SeatAllocation.objects.create(
                        student=student,
                        schedule=schedule,
                        classroom=room,
                        bench_number=bench_counter,
                        seat_position="single"
                    )
                    bench_counter += 1
                    break
                else:
                    bench_counter = 1
                    continue

    @transaction.atomic
    def allocate_mixed(sem_a, sem_b):
        nonlocal bench_counter

        list_a = list(Student.objects.filter(semester__number=sem_a).order_by("usn"))
        list_b = list(Student.objects.filter(semester__number=sem_b).order_by("usn"))

        max_len = max(len(list_a), len(list_b))

        i = 0
        j = 0

        for room in classrooms:
            bench_counter = 1

            while bench_counter <= room.num_benches and (i < len(list_a) or j < len(list_b)):

                # LEFT SEAT → semester A
                if i < len(list_a):
                    SeatAllocation.objects.create(
                        student=list_a[i],
                        schedule=schedule,
                        classroom=room,
                        bench_number=bench_counter,
                        seat_position="left"
                    )
                i += 1

                # RIGHT SEAT → semester B
                if j < len(list_b):
                    SeatAllocation.objects.create(
                        student=list_b[j],
                        schedule=schedule,
                        classroom=room,
                        bench_number=bench_counter,
                        seat_position="right"
                    )
                j += 1

                bench_counter += 1

            if i >= len(list_a) and j >= len(list_b):
                break

    # CASE 1 — MIXED SEMESTERS (e.g. 3rd + 5th same time)
    if len(mixed_semesters) == 2:
        sem1 = mixed_semesters[0]
        sem2 = mixed_semesters[1]

        allocate_mixed(sem1, sem2)

    # CASE 2 — ONLY THIS SEMESTER HAS EXAM
    else:
        allocate_single_sem(students)

    return JsonResponse({
        "status": "success",
        "message": "Seating allocation completed",
        "schedule": schedule_id
    })
