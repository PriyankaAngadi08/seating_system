from django.urls import path
from .views_seating import generate_seating

app_name = "seating"

urlpatterns = [
    path('generate/<int:schedule_id>/', generate_seating, name='generate_seating'),
]
