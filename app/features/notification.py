from plyer import notification
import datetime
import threading

def schedule_medication_notification(med_name, time_to_take, days):
    # Calculate the time difference from now to the medication time
    now = datetime.datetime.now()
    med_time = datetime.datetime.strptime(time_to_take, '%H:%M')
    med_time = now.replace(hour=med_time.hour, minute=med_time.minute, second=0, microsecond=0)
    delay = (med_time - now).total_seconds()
    print(now, med_time, delay)
    if delay > 0:
        # Check if today is a day for medication
        today = now.strftime('%a')  # Get current day in abbreviated format (e.g., 'Mon', 'Tue', etc.)
        if today in days and days[today] == 1:
            # Schedule the notification
            timer = threading.Timer(delay, send_notification_med, args=[med_name])
            timer.start()
            print("Scheduling notification for", med_name, "on", today,"at", med_time.strftime('%H:%M'))
        else:
            print("Today is not a day for", med_name)
    else:
        print("Time has already passed for", med_name)


def send_notification_med(med_name):
    notification.notify(title='Medication Reminder', message=f'Time to take your medication: {med_name}')
    print("Sending notification for", med_name)

def send_notification_apt(patient_name):
    notification.notify(title='Appointment Reminder', message=f'Time for your appointment with: {patient_name}')
    print(f"Notification sent to {patient_name}")

def schedule_notification(p_name, delay):
    timer = threading.Timer(delay, send_notification_apt, args=[p_name])
    print(f"Scheduling notification for {p_name} in {delay} seconds")
    timer.start()

def schedule_appointment_notification(p_name, time_to_take, date):
    appointment_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    today_date = datetime.datetime.now().date()

    if appointment_date.date() == today_date:
        now = datetime.datetime.now()
        med_time = datetime.datetime.strptime(time_to_take, '%H:%M')
        med_time = med_time.replace(year=now.year, month=now.month, day=now.day)
        
        delay = (med_time - now).total_seconds()

        if 0 <= delay <= 1 * 60:
            send_notification_apt(p_name)
        elif delay > 0:
            schedule_notification(p_name, delay)
        else:
            print("The time for the appointment has already passed.")
    else:
        print("The specified date is not today.")

