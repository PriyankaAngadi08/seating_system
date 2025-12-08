# seating/views_seating.py

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import (
    ExamSchedule,
    SeatAllocation,
    Classroom,
    Student,
)


def _students_for_semester_number(sem_number):
    """Return queryset/list of Student objects for a Semester number, ordered by USN."""
    return list(Student.objects.filter(semester__number=sem_number).order_by('usn'))


@transaction.atomic
def generate_seating(request, schedule_id):
    """
    Generate seating for the given ExamSchedule id.

    Behavior:
      - Auto-assign classrooms ordered by room_number (ascending).
      - If two semesters share the exact same exam_day + start_time + end_time,
        they are paired: left = lower-number semester, right = higher-number semester.
      - If only one semester is present at that slot, each bench is single (seat_side='S').
      - When a classroom's benches are exhausted, continue to next classroom.
      - Existing SeatAllocation rows for this exam_schedule are deleted before generation.
    """

    schedule = get_object_or_404(ExamSchedule, id=schedule_id)

    # find all schedules that are at the same day + exact same time window
    same_slot_qs = ExamSchedule.objects.filter(
        exam_day=schedule.exam_day,
        start_time=schedule.start_time,
        end_time=schedule.end_time,
    ).order_by('id')

    # Determine distinct semester numbers participating in this slot
    sem_numbers = sorted(
        set(same_slot_qs.values_list('subject__semester__number', flat=True))
    )

    # Classrooms in auto order (room_number ascending). If room_number is text, ensure desired ordering.
    classrooms = list(Classroom.objects.all().order_by('room_number'))

    if not classrooms:
        return JsonResponse({"status": "error", "message": "No classrooms defined"}, status=400)

    # Clear previous allocations for this exact schedule (to allow re-generate)
    SeatAllocation.objects.filter(exam_schedule=schedule).delete()

    allocations_to_create = []

    # Helper: iterate classrooms, benches, and generate SeatAllocation objects (appended then bulk_create)
    def allocate_single_sem(students):
        """One student per bench (seat_side='S')."""
        idx = 0
        for room in classrooms:
            for bench in range(1, room.benches + 1):
                if idx >= len(students):
                    return
                student = students[idx]
                allocations_to_create.append(
                    SeatAllocation(
                        student=student,
                        exam_schedule=schedule,
                        classroom=room,
                        bench_number=bench,
                        seat_side='S',  # single occupant
                    )
                )
                idx += 1

    def allocate_paired(sem_a, sem_b):
        """
        Pair sem_a -> Left (L) and sem_b -> Right (R) on same bench.
        If one list is longer, remaining students are put on Left (L) positions only.
        """
        list_a = _students_for_semester_number(sem_a)  # left
        list_b = _students_for_semester_number(sem_b)  # right

        ia = 0
        ib = 0

        # walk through rooms
        for room in classrooms:
            for bench in range(1, room.benches + 1):
                placed = False

                # PLACE left (sem_a) if available
                if ia < len(list_a):
                    allocations_to_create.append(
                        SeatAllocation(
                            student=list_a[ia],
                            exam_schedule=schedule,
                            classroom=room,
                            bench_number=bench,
                            seat_side='L',
                        )
                    )
                    ia += 1
                    placed = True

                # PLACE right (sem_b) if available
                if ib < len(list_b):
                    allocations_to_create.append(
                        SeatAllocation(
                            student=list_b[ib],
                            exam_schedule=schedule,
                            classroom=room,
                            bench_number=bench,
                            seat_side='R',
                        )
                    )
                    ib += 1
                    placed = True

                # if no student in either list, we may finish early
                if ia >= len(list_a) and ib >= len(list_b):
                    return

        # if after walking all rooms still students remain (rare if not enough benches),
        # continue assigning by creating extra benches in no room — but ideally classrooms should be enough.
        # Here we simply stop (you can add more classrooms in admin).
        return

    # Decide allocation path based on sem_numbers
    if len(sem_numbers) == 0:
        return JsonResponse({"status": "error", "message": "No semester found for this schedule"}, status=400)

    # If exactly 2 distinct semesters at same slot -> pair them
    if len(sem_numbers) == 2:
        sem_a, sem_b = sem_numbers[0], sem_numbers[1]
        allocate_paired(sem_a, sem_b)

    # If only 1 semester present -> single occupancy per bench
    elif len(sem_numbers) == 1:
        sem = sem_numbers[0]
        students = _students_for_semester_number(sem)
        allocate_single_sem(students)

    # If more than 2 semesters share a time (unlikely), we default to single-seat allocation for each semester in order:
    else:
        # flatten students in sem order and allocate single bench per student
        combined = []
        for sem in sem_numbers:
            combined.extend(_students_for_semester_number(sem))
        allocate_single_sem(combined)

    # Bulk create allocations
    if allocations_to_create:
        SeatAllocation.objects.bulk_create(allocations_to_create)

    return JsonResponse({
        "status": "success",
        "message": "Seating allocation generated",
        "created": len(allocations_to_create),
        "schedule_id": schedule_id,
    })
