from django.utils import timezone
from django import forms
from django.core.exceptions import ValidationError
from sender.models import Mailing, Client, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ('frequency', 'time_start', 'time_end', 'message', 'client')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        if self.request and self.request.user:
            user = self.request.user
            self.fields['client'].queryset = Client.objects.filter(owner=user)
            self.fields['message'].queryset = Message.objects.filter(owner=user)

    def clean(self):
        cleaned_data = super().clean()
        time_start = cleaned_data.get("time_start")
        time_end = cleaned_data.get("time_end")

        if time_start and time_end:
            if time_start < timezone.now():
                raise ValidationError('Время старта не может быть в прошлом')

            if time_end < time_start:
                raise ValidationError('Время окончания должно быть позже времени старта')

        return cleaned_data


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('email', 'first_name', 'surname', 'last_name', 'comment')


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('subject', 'body')
