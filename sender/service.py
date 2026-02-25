from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import logging
from .models import Mailing, Log

logger = logging.getLogger(__name__)


def send_mailing(mailing=None):
    """Отправляет либо одну рассылку, либо все подходящие по времени"""

    now = timezone.now()

    if mailing:
        mailings = [mailing]
    else:
        now = timezone.now()
        mailings = Mailing.objects.filter(
            time_start__lte=now,
            time_end__gte=now,
            status__in=['started', 'created']
        )

    for m in mailings:
        if m.status == 'created':
            m.status = 'started'
            m.save()

        if not mailing:
            last_log = Log.objects.filter(mailing=m, status='success').order_by('-created_at').first()
            if last_log:
                delta = timedelta(days=0)
                if m.frequency == 'daily':
                    delta = timedelta(days=1)
                elif m.frequency == 'weekly':
                    delta = timedelta(days=7)
                elif m.frequency == 'monthly':
                    delta = timedelta(days=30)

                if now < last_log.created_at + delta:
                    continue

        try:
            send_mail(
                subject=m.message.subject,
                message=m.message.body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email for client in m.client.all()],
                fail_silently=False,
            )
            logger.info(f"Рассылка {m.pk} успешно отправлена на {m.client.count()} адресов")
            Log.objects.create(
                status='success',
                mailing=m,
                server_response='Письмо успешно отправлено'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки рассылки {m.pk}: {str(e)}")
            Log.objects.create(
                status='error',
                mailing=m,
                server_response=str(e)
            )

    expired_mailings = Mailing.objects.filter(time_end__lt=now, status='started')
    expired_mailings.update(status='done')
