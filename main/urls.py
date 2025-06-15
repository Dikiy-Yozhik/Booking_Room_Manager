# booking_project/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Booking_Room_Manager.urls')),
    path('accounts/', include('accounts.urls')),
]