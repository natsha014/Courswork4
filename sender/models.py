from django.utils import timezone

from django.db import models
from django.conf import settings


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Отчество')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    comment = models.TextField(verbose_name='Комментарий')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        permissions = [
            ('view_all_clients', 'Может просматривать любых клиентов'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.surname} {self.last_name} ({self.email})"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Тема сообщения')
    body = models.TextField(verbose_name='Содержание сообщения')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        permissions = [
            ('view_all_messages', 'Может просматривать любые сообщения'),
        ]

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('done', 'Завершена'),
    ]
    FREQUENCY_CHOICES = [
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц'),
    ]
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='Периодичность',
                                 default='daily')
    time_start = models.DateTimeField(verbose_name='Дата и время старта')
    time_end = models.DateTimeField(verbose_name='Дата и время окончания')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус', default='created')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='mailings')
    client = models.ManyToManyField(Client, related_name='mailings')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name='Владелец',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            ('can_view_any_mailing', 'Может просматривать любые рассылки'),
            ('can_disable_mailing', 'Может блокировать любые рассылки'),
        ]

    def update_status(self):
        now = timezone.now()
        if now < self.time_start:
            self.status = "created"
        elif self.time_start <= now <= self.time_end:
            self.status = "started"
        else:
            self.status = "done"
        self.save()

    def __str__(self):
        return f'Рассылка {self.pk}: {self.message.subject} ({self.get_status_display()})'


class Log(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('error', 'Ошибка'),
    ]

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время попытки')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs')
    server_response = models.TextField(verbose_name='Ответ сервера', blank=True, null=True)

    class Meta:
        verbose_name = 'Лог рассылки'
        verbose_name_plural = 'Логи рассылки'

    def __str__(self):
        return f'{self.mailing}, статус: {self.status}'
