from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView, toggle_user_active, UserListView, ProfileView, ProfileEditView
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='sender:main'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user/toggle/<int:pk>/', toggle_user_active, name='toggle_user'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('toggle-active/<int:pk>/', toggle_user_active, name='toggle_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),
]
