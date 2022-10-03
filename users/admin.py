from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Venue

admin.site.register(Venue)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {'fields': ('password',)}),
        (_('Name'), {'fields': ('first_name', 'last_name', 'patronymic_name')}),
        (
            _('Private'),
            {'fields': ('gender', 'birth_date', 'passport', 'school', 'actual_form')},
        ),
        (_('Participant'), {'fields': ('participation_form', 'venue_selected')}),
        (_('Contact'), {'fields': ('email', 'phone', 'city')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )
    list_display = (
        'email',
        'first_name',
        'last_name',
        'patronymic_name',
        'city',
        'is_staff',
    )
    search_fields = ('email', 'first_name', 'last_name', 'city', 'school', 'phone')
    ordering = ('email', 'first_name', 'city')
