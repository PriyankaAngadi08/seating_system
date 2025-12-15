from django.db import models


# --------------------------
# SEMESTER
# --------------------------
class Semester(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Semester {self.number}"


# --------------------------
# STUDENT
# --------------------------
class Student(models.Model):
    usn = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=50)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.usn})"


# --------------------------
# CLASSROOM
# --------------------------
class Classroom(models.Model):
    room_number = models.CharField(max_length=10)
    benches = models.IntegerField()   # total benches

    def __str__(self):
        return f"{self.room_number} ({self.benches} benches)"


# --------------------------
# EXAM DAY
# --------------------------
class ExamDay(models.Model):
    date = models.DateField(unique=True)

    def __str__(self):
        return f"Exam Day {self.date}"


# --------------------------
# EXAM SUBJECT (subject offered for a semester)
# Example: DS(3rd sem), DBMS(5th sem)
# --------------------------
class ExamSubject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subject_name} (Sem {self.semester.number})"


# --------------------------
# EXAM SCHEDULE
# Multiple subjects per day, per semester
# Example: Day1 → DS(3) at 9am, Python(3) at 11am, DBMS(5) at 2pm
# --------------------------
class ExamSchedule(models.Model):
    exam_day = models.ForeignKey(ExamDay, on_delete=models.CASCADE)
    subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.exam_day.date} - {self.subject.subject_name}"


# --------------------------
# SEAT ALLOCATION
# Stores final seating result
# --------------------------
# seating/models.py  (only the SeatAllocation model below — replace existing SeatAllocation)
from django.db import models

SEAT_SIDE_CHOICES = (
    ('L', 'Left'),
    ('R', 'Right'),
    ('S', 'Single'),  # Single occupant on the bench (used when only one-semester exam)
)

class SeatAllocation(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    exam_schedule = models.ForeignKey('ExamSchedule', on_delete=models.CASCADE, related_name='allocations')
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE)
    bench_number = models.IntegerField()
    seat_side = models.CharField(max_length=1, choices=SEAT_SIDE_CHOICES, default='L')
    emailed = models.BooleanField(default=False)   # mark once email is sent
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exam_schedule', 'classroom', 'bench_number', 'seat_side')
        ordering = ('exam_schedule__exam_day__date', 'classroom__id', 'bench_number', 'seat_side')

    def __str__(self):
        side = dict(SEAT_SIDE_CHOICES).get(self.seat_side, self.seat_side)
        return f"{self.student.usn} -> {self.classroom.room_number} bench {self.bench_number} ({side})"

