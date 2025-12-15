from django.urls import path
from .views_seating import generate_seating, preview_seating, send_emails
from .views_seating import frontend_test
from .views_seating import home
from . import views

app_name = "seating"


urlpatterns = [
    path("classroom/<int:schedule_id>/", views.virtual_classroom, name="virtual_classroom"),
    path("", home, name="home"),

     path(
        "classroom/<int:classroom_id>/",
        views.classroom_layout_view,
        name="classroom_layout"
    ),
    path(
        "generate/<int:schedule_id>/",
        generate_seating,
        name="generate_seating",
    ),

    path(
        "preview/<int:schedule_id>/",
        preview_seating,
        name="preview_seating",
    ),

    path(
        "send-emails/<int:schedule_id>/",
        send_emails,
        name="send_emails",
    ),
    path(
    "test-frontend/",
    frontend_test,
    name="test_frontend",
),

]
