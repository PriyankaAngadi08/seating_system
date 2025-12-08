from django.contrib import admin
from django.urls import path, include
from seating.views import home   # 👈 Import home function

urlpatterns = [
    path('', home, name='home'),   # 👈 Homepage route
    path('admin/', admin.site.urls),
    path('seating/', include('seating.urls')),
]

