# seating/utils.py
from .models import Student, Classroom, SeatAllocation, ExamSchedule

def generate_seating_allocation(schedule: ExamSchedule):
    """
    Generate seating plan for a given exam schedule.
    Conditions:
        ✔ If two semesters have exam at same time → pair them left-right per bench
        ✔ If only one semester has exam → only one student per bench
        ✔ Continue to next room if one room is full
    """

    subject = schedule.subject
    exam_day = schedule.exam_day
    semester = subject.semester  

    # 1️⃣ Get all students of this semester
    students = list(
        Student.objects.filter(semester=semester).order_by("usn")
    )

    if not students:
        return "No students found!"

    # 2️⃣ Determine pairing logic
    # Get other schedules on the same day & same timeslot
    parallel_schedules = ExamSchedule.objects.filter(
        exam_day=exam_day,
        start_time=schedule.start_time,
        end_time=schedule.end_time
    ).exclude(id=schedule.id)

    paired = False
    other_sem_students = []

    if parallel_schedules.exists():
        # Assume only 2 sems at same time (3rd + 5th)
        other_sem = parallel_schedules.first().subject.semester
        other_sem_students = list(
            Student.objects.filter(semester=other_sem).order_by("usn")
        )
        paired = True

    # 3️⃣ Get classrooms sorted by room number
    rooms = Classroom.objects.all().order_by("room_number")

    if not rooms:
        return "No classrooms found!"

    # Clean previous allocations for this schedule
    SeatAllocation.objects.filter(schedule=schedule).delete()

    allocations = []
    student_index = 0
    other_index = 0

    # 4️⃣ Loop through rooms & benches
    for room in rooms:
        for bench in range(1, room.benches + 1):

            if paired:
                # Two students per bench
                left_student = students[student_index] if student_index < len(students) else None
                right_student = other_sem_students[other_index] if other_index < len(other_sem_students) else None

                if left_student:
                    allocations.append(SeatAllocation(
                        schedule=schedule,
                        student=left_student,
                        classroom=room,
                        bench_number=bench,
                        position="L"
                    ))
                    student_index += 1

                if right_student:
                    allocations.append(SeatAllocation(
                        schedule=schedule,
                        student=right_student,
                        classroom=room,
                        bench_number=bench,
                        position="R"
                    ))
                    other_index += 1

                # Stop if no one left
                if student_index >= len(students) and other_index >= len(other_sem_students):
                    break

            else:
                # Only one student per bench
                if student_index < len(students):
                    allocations.append(SeatAllocation(
                        schedule=schedule,
                        student=students[student_index],
                        classroom=room,
                        bench_number=bench,
                        position="L"
                    ))
                    student_index += 1
                else:
                    break

        if student_index >= len(students) and (not paired or other_index >= len(other_sem_students)):
            break

    # Save all seat allocations
    SeatAllocation.objects.bulk_create(allocations)

    return f"Seating generated for {schedule.subject.subject_name}"
