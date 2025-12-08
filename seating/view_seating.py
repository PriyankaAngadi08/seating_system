ffrom django.http import JsonResponse
from seating.models import Student, ExamSchedule, Classroom, SeatAllocation

def generate_seating(request, schedule_id):

    """
    Generate seating arrangement for a given ExamSchedule.
    """
    schedule = ExamSchedule.objects.get(id=schedule_id)
    subject = schedule.subject
    semester = subject.semester
    exam_day = schedule.day

    # STEP 1: Get all students of that semester
    students = list(Student.objects.filter(semester=semester).order_by('usn'))

    # STEP 2: Get all classrooms ordered by room number
    classrooms = Classroom.objects.all().order_by('room_number')

    # STEP 3: Clear old allocations for this subject on this day & slot
    SeatAllocation.objects.filter(
        student__semester=semester,
        subject=subject,
        exam_day=exam_day,
        time_slot=schedule
    ).delete()

    allocations = []
    student_index = 0

    # STEP 4: Fill classrooms one by one
    for room in classrooms:
        bench_capacity = room.benches

        for bench in range(1, bench_capacity + 1):
            if student_index >= len(students):
                break

            student = students[student_index]
            student_index += 1

            allocations.append(
                SeatAllocation(
                    student=student,
                    subject=subject,
                    exam_day=exam_day,
                    time_slot=schedule,
                    classroom=room,
                    bench_number=bench,
                    side="Full bench"  # since single sem exam → whole bench used
                )
            )

        if student_index >= len(students):
            break

    SeatAllocation.objects.bulk_create(allocations)

    return JsonResponse({
        "status": "success",
        "allocated": len(allocations),
        "students_total": len(students),
        "message": "Seating generated successfully"
    })
