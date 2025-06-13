# bd/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from datetime import time

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name



class TimeSlot(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.room.name} | {self.date} | {self.start_time}-{self.end_time}"



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        overlapping = Booking.objects.filter(
            room=self.room,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            is_active=True
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError("Этот временной слот занят.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def cancel_booking(self):
        self.is_active = False
        self.save()
        send_mail(
            "Бронь отменена",
            f"Ваша бронь комнаты {self.room.name} на {self.date} с {self.start_time} отменена.",
            "noreply@example.com",
            [self.user.email],
            fail_silently=False,
        )