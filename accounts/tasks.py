from datetime import timedelta
from django.utils import timezone
from .models import Booking
from django.core.mail import send_mail

def check_upcoming_bookings():
    now = timezone.now()
    upcoming = Booking.objects.filter(
        date=now.date(),
        start_time__gte=(now - timedelta(minutes=30)).time(),
        start_time__lte=now.time(),
        is_active=True
    )
    for b in upcoming:
        send_mail(
            "Напоминание о бронировании",
            f"Через 30 минут начнётся ваша бронь: комната {b.room}, дата {b.date}, время {b.start_time}.",
            "noreply@example.com",
            [b.user.email],
            fail_silently=False
        )