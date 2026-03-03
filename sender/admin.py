from django.contrib import admin
from .models import Mailing, Client, Message, Log


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('time_start', 'status', 'display_clients', 'message', 'owner')

    def display_clients(self, obj):
        """Создает строку из email-адресов клиентов для отображения в списке"""
        return ", ".join([client.email for client in obj.client.all()])

    display_clients.short_description = 'Клиенты'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'owner')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'owner')


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'created_at', 'status')
