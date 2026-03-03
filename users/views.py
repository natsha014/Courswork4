from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DetailView
from django.views.generic.edit import CreateView

from django.conf import settings
from .forms import UserRegisterForm, UserProfileForm
from .models import User
from django.core.mail import send_mail
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    permission_required = 'users.view_user'


@permission_required('users.can_block_user')
def toggle_user_active(request, pk):
    """Менеджер блокирует/разблокирует пользователя"""
    user_to_edit = get_object_or_404(User, pk=pk)

    if not user_to_edit.is_superuser:
        user_to_edit.is_active = not user_to_edit.is_active
        user_to_edit.save()

    return redirect('user:user_list')


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в наш сервис'
        message = 'Спасибо, что зарегистрировались в нашем сервисе!'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=True
        )


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile_detail.html'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'sender/common_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
