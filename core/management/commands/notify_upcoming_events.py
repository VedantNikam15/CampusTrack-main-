from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event, Notification, User
from django.conf import settings
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Notify users about upcoming events. Avoids duplicating notifications by checking for existing similar messages.'

    def add_arguments(self, parser):
        parser.add_argument('--hours', type=int, default=24, help='Look ahead this many hours for upcoming events')
        parser.add_argument('--type', choices=['start','registration'], default='start', help='Type of reminder: start or registration')

    def handle(self, *args, **options):
        hours = options['hours']
        typ = options['type']
        now = timezone.now()
        end = now + timezone.timedelta(hours=hours)
        events = Event.objects.filter(date_from__gte=now, date_from__lte=end)
        count = 0
        for ev in events:
            if typ == 'start':
                content = f'Event "{ev.title}" starting soon on {ev.date_from.strftime("%b %d %Y %H:%M")}.'
                check_exists = Notification.objects.filter(content__icontains=f'Event "{ev.title}" starting soon').exists()
            else:
                content = f'Registration reminder: "{ev.title}" starts on {ev.date_from.strftime("%b %d %Y %H:%M")}. Please register.'
                check_exists = Notification.objects.filter(content__icontains=f'Registration reminder: "{ev.title}"').exists()

            if check_exists:
                continue

            # choose recipients
            if ev.scope == 'college':
                targets = User.objects.filter(role='student')
            else:
                targets = User.objects.filter(role='student', department=ev.department)

            for u in targets:
                Notification.objects.create(user=u, content=content)
                try:
                    if getattr(settings, 'EMAIL_HOST', None) and u.email:
                        send_mail(f'Event Reminder: {ev.title}', content, settings.DEFAULT_FROM_EMAIL, [u.email], fail_silently=True)
                except Exception:
                    pass
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Sent {count} notifications for {events.count()} events (type={typ})'))
