from django.core.management.base import BaseCommand
from sender.service import send_mailing


class Command(BaseCommand):
    help = 'Запуск рассылки писем'

    def handle(self, *args, **options):
        send_mailing()
        self.stdout.write(self.style.SUCCESS('Рассылка выполнена! Проверьте логи.'))
