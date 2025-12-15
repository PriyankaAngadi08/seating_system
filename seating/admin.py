from django.urls import reverse
from django.utils.html import format_html


from django.contrib import admin
from .models import (
    Semester, Student, Classroom, ExamDay,
    ExamSubject, ExamSchedule, SeatAllocation
)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("number",)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("usn", "name", "email", "department", "semester")
    search_fields = ("usn", "name")

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "benches")

@admin.register(ExamDay)
class ExamDayAdmin(admin.ModelAdmin):
    list_display = ("date",)

@admin.register(ExamSubject)
class ExamSubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_name", "semester")

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "exam_day", "subject", "start_time", "end_time", "generate_button")
    list_filter = ("exam_day", "subject__semester")
    search_fields = ("subject__subject_name",)

    def generate_button(self, obj):
        url = reverse("seating:generate_seating", args=[obj.id])
        return format_html('<a class="button" href="{}" target="_blank">Generate Seating</a>', url)
    generate_button.short_description = "Generate"
    generate_button.allow_tags = True


@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "exam_schedule",
        "classroom",
        "bench_number",
        "seat_side",
        "emailed",
        "timestamp",
    )

    list_filter = ("exam_schedule__exam_day", "classroom", "seat_side")
    search_fields = ("student__usn", "student__name")
