from django.urls import path
from sender.apps import SenderConfig
from sender.views import MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView, \
    MessageDetailView, MailingListView, ClientListView, ClientDetailView, MainView, MessageListView, \
    MessageUpdateView, MessageDeleteView, ClientCreateView, ClientUpdateView, ClientDeleteView, LogListView, \
    MessageCreateView, toggle_mailing_status, start_mailing_view
from django.views.decorators.cache import cache_page

app_name = SenderConfig.name

urlpatterns = [
    path('', MainView.as_view(), name='main'),

    path('sender/list/', cache_page(60)(MailingListView.as_view()), name='mailing_list'),
    path('sender/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('sender/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('sender/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('sender/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),

    path('message/list/', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    path('client/list/', ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('client/create/', ClientCreateView.as_view(), name='client_create'),
    path('client/<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('client/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),

    path('logs/', LogListView.as_view(), name='log_list'),
    path('mailing/toggle/<int:pk>/', toggle_mailing_status, name='toggle_mailing'),
    path('mailing/start/<int:pk>/', start_mailing_view, name='start_mailing'),
]
