from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Booking_Room_Manager.models import Room, Booking, TimeSlot
from Booking_Room_Manager.forms import BookingForm
from django.utils import timezone
from datetime import datetime, timedelta, time


def home(request):
    is_authenticated = request.user.is_authenticated
    is_teacher = is_authenticated and request.user.userprofile.role == 'teacher'

    context = {
        'is_authenticated': is_authenticated,
        'is_teacher': is_teacher,
    }
    return render(request, 'Booking_Room_Manager/home.html', context)


def calendar_view(request):
    rooms = Room.objects.all()
    today = timezone.now().date()
    times = [time(h, 0) for h in range(9, 18)] 
    bookings = Booking.objects.filter(date=today, is_active=True)

    time_slots = []

    for t in times:
        row = {'time': t.strftime("%H:%M"), 'rooms': []}
        for room in rooms:
            is_booked = bookings.filter(room=room, start_time=t).exists()
            row['rooms'].append({
                'name': room.name,
                'id': room.id,
                'booked': is_booked
            })
        time_slots.append(row)

    context = {
        'time_slots': time_slots,
        'today': today
    }

    return render(request, 'Booking_Room_Manager/calendar.html', context)


@login_required
def reschedule_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        new_time = request.POST.get('new_time')
        new_end_time = request.POST.get('new_end_time')
        new_date = request.POST.get('new_date')

        try:
            # Преобразуем строки времени в объекты time
            start_time_obj = datetime.strptime(new_time, "%H:%M").time()
            end_time_obj = datetime.strptime(new_end_time, "%H:%M").time()

            # Проверяем, что время окончания позже времени начала
            if end_time_obj <= start_time_obj:
                messages.error(request, "Время окончания должно быть позже времени начала")
                return redirect('reschedule_booking', booking_id=booking.id)

            # Обновляем бронь
            booking.date = new_date
            booking.start_time = start_time_obj
            booking.end_time = end_time_obj
            booking.save()

            messages.success(request, "Бронь успешно перенесена!")
            return redirect('profile_view')

        except ValueError:
            messages.error(request, "Неверный формат времени. Используйте ЧЧ:ММ")
        except Exception as e:
            messages.error(request, f"Ошибка: {str(e)}")

    return render(request, 'Booking_Room_Manager/reschedule.html', {
        'booking': booking
    })

@login_required
def book_room(request):
    initial = {}

    room_id = request.GET.get('room')
    selected_time_str = request.GET.get('time')

    if room_id:
        initial['room'] = room_id

    if selected_time_str:
        today = timezone.now().date()
        try:
            parsed_time = datetime.strptime(selected_time_str, "%H:%M").time()
        except ValueError:
            try:
                parsed_time = datetime.strptime(selected_time_str, "%I %p").time()
            except ValueError:
                parsed_time = None

        if parsed_time:
            initial['date'] = today
            initial['start_time'] = parsed_time
            initial['end_time'] = (
                datetime.combine(today, parsed_time) + timedelta(hours=1)
            ).time()

    form = BookingForm(initial=initial)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            try:
                booking.save()
                messages.success(request, "Комната успешно забронирована!")
                return redirect('profile_view')
            except Exception as e:
                messages.error(request, str(e))

    return render(request, 'Booking_Room_Manager/book_form.html', {'form': form})


@login_required
def cancel_booking(request, booking_id):
    try:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        booking.delete()
        return redirect('profile_view')
    except Exception as e:
        messages.error(request, f"Ошибка при удалении брони: {str(e)}")
        return redirect('profile_view')


@login_required
def profile_view(request):
    bookings = Booking.objects.filter(
        user=request.user, is_active=True).order_by('-date')

    is_authenticated = request.user.is_authenticated
    is_teacher = is_authenticated and request.user.userprofile.role == 'teacher'

    return render(request, 'Booking_Room_Manager/profile.html', {'bookings': bookings,
                                                                 'is_teacher': is_teacher,})