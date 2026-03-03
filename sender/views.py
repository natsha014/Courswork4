from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .forms import MailingForm, ClientForm, MessageForm
from .models import Client, Message, Log
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from users.models import User
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from .models import Mailing
from .service import send_mailing
from django.contrib import messages


@permission_required('sender.can_disable_mailing')
def toggle_mailing_status(request, pk):
    """Менеджер отключает рассылку (переводит в статус 'done')"""
    mailing = get_object_or_404(Mailing, pk=pk)
    if mailing.status != 'done':
        mailing.status = 'done'
    else:
        mailing.status = 'created'
    mailing.save()
    return redirect('sender:mailing_list')


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    permission_required = 'users.can_view_any_user'


class OwnerQuerySetMixin:
    """Миксин для фильтрации объектов по владельцу"""

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(owner=self.request.user)


class OwnerFormValidMixin:
    """Миксин для автоматической привязки владельца при создании объекта"""

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ManagerListDetailMixin:

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser or user.has_perm('sender.view_all_messages') or \
                user.has_perm('sender.view_all_clients') or user.has_perm('sender.can_view_any_mailing'):
            return queryset
        return queryset.filter(owner=user)


class ClientListView(LoginRequiredMixin, ManagerListDetailMixin, ListView):
    model = Client


class ClientDetailView(LoginRequiredMixin, ManagerListDetailMixin, DetailView):
    model = Client


class ClientCreateView(LoginRequiredMixin, OwnerFormValidMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:client_list')


class ClientUpdateView(LoginRequiredMixin, OwnerQuerySetMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:client_list')


class ClientDeleteView(LoginRequiredMixin, OwnerQuerySetMixin, DeleteView):
    model = Client
    template_name = 'sender/confirm_delete.html'
    success_url = reverse_lazy('sender:client_list')


class MessageListView(LoginRequiredMixin, ManagerListDetailMixin, ListView):
    model = Message


class MessageDetailView(LoginRequiredMixin, ManagerListDetailMixin, DetailView):
    model = Message


class MessageCreateView(LoginRequiredMixin, OwnerFormValidMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:message_list')


class MessageUpdateView(LoginRequiredMixin, OwnerQuerySetMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:message_list')


class MessageDeleteView(LoginRequiredMixin, OwnerQuerySetMixin, DeleteView):
    model = Message
    template_name = 'sender/confirm_delete.html'
    success_url = reverse_lazy('sender:message_list')


class MailingListView(LoginRequiredMixin, ManagerListDetailMixin, ListView):
    model = Mailing


class MailingDetailView(LoginRequiredMixin, ManagerListDetailMixin, DetailView):
    model = Mailing

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # ← пересчёт и сохранение статуса
        return obj


class MailingCreateView(LoginRequiredMixin, OwnerFormValidMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:main')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class MailingUpdateView(LoginRequiredMixin, OwnerQuerySetMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('sender:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class MailingDeleteView(LoginRequiredMixin, OwnerQuerySetMixin, DeleteView):
    model = Mailing
    template_name = 'sender/confirm_delete.html'
    success_url = reverse_lazy('sender:mailing_list')


class LogListView(LoginRequiredMixin, ListView):
    model = Log
    template_name = 'sender/log_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        return queryset.filter(mailing__owner=self.request.user)


class MainView(TemplateView):
    template_name = 'sender/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mailings_total'] = Mailing.objects.count()
        context['mailings_active'] = Mailing.objects.filter(status="started").count()
        context['clients_unique'] = Client.objects.distinct().count()

        return context


def start_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if request.user == mailing.owner or request.user.is_staff:
        send_mailing(mailing)
        messages.success(request, f'Рассылка "{mailing.message.subject}" отправлена!')
    else:
        messages.error(request, 'У вас недостаточно прав.')

    return redirect('sender:mailing_detail', pk=pk)
