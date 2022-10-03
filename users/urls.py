from django.contrib.auth import views as auth_views
from django.urls import path

from . import forms, views

urlpatterns = [
    path(r'update/', views.UserUpdateView.as_view(), name='profile'),
    path(
        r'login/',
        auth_views.LoginView.as_view(
            template_name='login.html', form_class=forms.LoginForm
        ),
        name='login',
    ),
    path(r'logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            form_class=forms.PasswordResetForm, template_name='password_reset.html'
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(
            form_class=forms.PasswordChangeForm, template_name='password_change.html'
        ),
        name='password_change',
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='password_change_done.html'
        ),
        name='password_change_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=forms.SetPasswordForm,
            template_name='password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),
]
