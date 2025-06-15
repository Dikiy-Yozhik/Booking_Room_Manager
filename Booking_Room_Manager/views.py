from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from Booking_Room_Manager.models import Room, Booking, TimeSlot
from Booking_Room_Manager.forms import BookingForm, RoomForm
from django.utils import timezone
from datetime import datetime, timedelta, time

from django.http import HttpResponse
import csv


def home(request):
    is_authenticated = request.user.is_authenticated
    is_teacher = is_authenticated and request.user.userprofile.role == 'teacher'
    is_admin = is_authenticated and request.user.userprofile.role == 'admin'

    context = {
        'is_authenticated': is_authenticated,
        'is_teacher': is_teacher,
        'is_admin' : is_admin,
    }
    return render(request, 'Booking_Room_Manager/home.html', context)


def calendar_view(request):
    rooms = Room.objects.all()
    today = timezone.now().date()
    week = [today + timedelta(days=i) for i in range(7)]
    times = [time(h, 0) for h in range(9, 18)]

    is_admin = request.user.userprofile.role == 'admin' if hasattr(request.user, 'userprofile') else False

    time_slots = []

    for d in week:
        day = []
        bookings = Booking.objects.filter(date=d, is_active=True)
        for t in times:
            row = {'time': t.strftime("%H:%M"), 'rooms': []}
            for room in rooms:
                booking = bookings.filter(room=room, start_time=t).first()
                is_booked = booking is not None
                is_blocked = is_booked and booking.is_blocked

                row['rooms'].append({
                    'name': room.name,
                    'id': room.id,
                    'booked': is_booked,
                    'blocked': is_blocked,
                    'booking_id': booking.id if booking else None
                })
            day.append(row)
        time_slots.append(day)

    # views.py
    context = {
        'days': zip(week, time_slots),  # Объединяем даты и слоты
        'today': today,
        'is_admin': is_admin
    }

    return render(request, 'Booking_Room_Manager/calendar.html', context)


@login_required
def block_slot(request, room_id, time, date):
    # Проверка прав администратора
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('calendar_view')

    try:
        room = Room.objects.get(id=room_id)
        start_time = datetime.strptime(time, "%H:%M").time()
        date = datetime.strptime(date, "%Y-%m-%d").date()
        end_time = (datetime.combine(date, start_time) + timedelta(hours=1)).time()

        # Проверка на существующие брони
        conflict = Booking.objects.filter(
            room=room,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            is_active=True
        ).exists()

        if conflict:
            messages.error(request, 'Найдены конфликтующие бронирования')
            return redirect('calendar_view')

        # Создание блокировки
        Booking.objects.create(
            room=room,
            user=request.user,
            date=date,
            start_time=start_time,
            end_time=end_time,
            is_blocked=True,
            is_active=True
        )
        messages.success(request, 'Временной слот заблокирован')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')

    return redirect('calendar_view')


@login_required
def unblock_slot(request, booking_id):
    # Проверка прав администратора
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, 'Доступ запрещен')
        return redirect('calendar_view')

    try:
        booking = Booking.objects.get(id=booking_id, is_blocked=True)
        booking.delete()
        messages.success(request, 'Блокировка снята')
    except Exception as e:
        messages.error(request, f'Ошибка: {str(e)}')

    return redirect('calendar_view')


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


# views.py
@login_required
def profile_view(request):
    is_authenticated = request.user.is_authenticated
    is_teacher = is_authenticated and request.user.userprofile.role == 'teacher'
    is_admin = is_authenticated and request.user.userprofile.role == 'admin'

    if is_admin:
        # Для администратора показываем все активные бронирования
        bookings = Booking.objects.filter(is_active=True).order_by('-date')
    else:
        # Для обычных пользователей только их бронирования
        bookings = Booking.objects.filter(
            user=request.user, is_active=True).order_by('-date')

    return render(request, 'Booking_Room_Manager/profile.html', {
        'bookings': bookings,
        'is_teacher': is_teacher,
        'is_admin': is_admin
    })


@login_required
def add_room(request):
    # Проверка прав администратора
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        messages.error(request, 'У вас нет прав для выполнения этого действия')
        return redirect('home')

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Комната успешно добавлена')
            return redirect('calendar_view')
    else:
        form = RoomForm()

    return render(request, 'Booking_Room_Manager/add_room.html', {'form': form})


@login_required
def export_bookings(request):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'admin':
        return redirect('home')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="bookings_{datetime.now().strftime("%Y-%m-%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Комната', 'Дата', 'Время начала', 'Время окончания', 'Пользователь', 'Цель'])

    bookings = Booking.objects.filter(is_active=True).select_related('room', 'user')
    for booking in bookings:
        writer.writerow([
            booking.room.name,
            booking.date.strftime("%d.%m.%Y"),
            booking.start_time.strftime("%H:%M"),
            booking.end_time.strftime("%H:%M"),
            booking.user.get_full_name() or booking.user.username,
        ])

    return response