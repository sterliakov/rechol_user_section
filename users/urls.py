from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import forms, views

api_urls = [
    path('annotations/list/', views.AnnotationList.as_view(), name='annotation_list'),
    path(
        'annotations/detail/<pk>/',
        views.AnnotationDetail.as_view(),
        name='annotation_detail',
    ),
]

online_stage_urls = [
    path(r'', views.OnlineStageListView.as_view(), name='online_submission_index'),
    path(
        r'start/<int:problem_pk>/',
        views.OnlineStageStartView.as_view(),
        name='online_submission_start',
    ),
    path(
        r'submit/<int:problem_pk>/',
        views.OnlineStageSubmitView.as_view(),
        name='online_submission_update',
    ),
    path(
        r'appeal/<int:problem_pk>/',
        views.OnlineAppellationView.as_view(),
        name='online_submission_appeal',
    ),
]

offline_stage_urls = [
    path(r'', views.AppellationView.as_view(), name='offline_appellation'),
]

venue_urls = [
    path(
        r'register/', views.VenueRegistrationView.as_view(), name='venue_registration'
    ),
    path(r'update/', views.VenueUpdateView.as_view(), name='venue_update'),
    path(r'list/', views.VenuesListView.as_view(), name='venues_list'),
]

urlpatterns = [
    path(r'reg/', views.RegistrationView.as_view(), name='registration'),
    path(
        r'judge_reg/', views.JudgeRegistrationView.as_view(), name='judge_registration'
    ),
    path(
        r'venue_registration/',
        views.VenueUserRegistrationView.as_view(),
        name='venue_user_registration',
    ),
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
    path('api/v1/', include(api_urls)),
    path('online/', include(online_stage_urls)),
    path('in_person/', include(offline_stage_urls)),
    path('venue/', include(venue_urls)),
]
