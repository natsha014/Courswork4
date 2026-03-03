from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

from users.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'avatar')
