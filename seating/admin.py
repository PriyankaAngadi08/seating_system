from django.contrib import admin
from .models import (
    Semester,
    Student,
    Classroom,
    ExamDay,
    ExamSubject,
    ExamSchedule,
    SeatAllocation
)

# -----------------------
# SEMESTER ADMIN
# -----------------------
@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("id", "number")
    search_fields = ("number",)


# -----------------------
# STUDENT ADMIN
# -----------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("usn", "name", "email", "department", "semester")
    search_fields = ("usn", "name", "email", "department")
    list_filter = ("semester", "department")


# -----------------------
# CLASSROOM ADMIN
# -----------------------
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "benches")
    search_fields = ("room_number",)


# -----------------------
# EXAM DAY ADMIN
# -----------------------
@admin.register(ExamDay)
class ExamDayAdmin(admin.ModelAdmin):
    list_display = ("id", "date")
    ordering = ("date",)


# -----------------------
# EXAM SUBJECT ADMIN
# -----------------------
@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "subject_name", "semester")
    list_filter = ("semester",)
    search_fields = ("subject_name",)


# -----------------------
# EXAM SCHEDULE ADMIN
# -----------------------
@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "exam_day", "subject", "start_time", "end_time")
    list_filter = ("exam_day", "subject__semester")
    search_fields = ("subject__subject_name",)


# -----------------------
# SEAT ALLOCATION ADMIN
# -----------------------
@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam_schedule",
        "classroom",
        "bench_number",
        "seat_side",
        "emailed"
    )
    list_filter = ("exam_schedule__exam_day", "classroom", "seat_side", "emailed")
    search_fields = ("student__usn", "student__name")
