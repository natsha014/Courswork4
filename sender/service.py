from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Mailing, Log


def send_mailing(mailing=None):
    """Отправляет либо одну рассылку, либо все подходящие по времени"""
    if mailing:
        mailings = [mailing]
    else:
        now = timezone.now()
        mailings = Mailing.objects.filter(
            time_start__lte=now,
            time_end__gte=now,
            status='started'
        )

    for m in mailings:
        try:
            send_mail(
                subject=m.message.subject,
                message=m.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email for client in m.client.all()],
                fail_silently=False,
            )
            Log.objects.create(
                status='success',
                mailing=m,
                server_response='Письмо успешно отправлено'
            )
        except Exception as e:
            Log.objects.create(
                status='error',
                mailing=m,
                server_response=str(e)
            )
