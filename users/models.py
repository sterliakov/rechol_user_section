from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as UserManager_
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Venue(models.Model):
    city = models.CharField(_('City'), max_length=63, blank=False, null=False)
    full_address = models.CharField(
        _('Address'), max_length=255, blank=False, null=False
    )

    def __str__(self):
        return f'{self.city} ({self.full_address})'


class UserManager(UserManager_):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(  # type: ignore[override]
        self, email: str, password: str, **extra_fields
    ):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(  # type: ignore[override]
        self, email: str, password: str, **extra_fields
    ):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class GenderChoices(models.TextChoices):
        MALE = 'm', _('Male')
        FEMALE = 'f', _('Female')

    class PossibleForms(models.IntegerChoices):
        EIGHT = 8, _('8')
        NINTH = 9, _('9')
        TENTH = 10, _('10')
        ELEVENTH = 11, _('11')
        OTHER = 1, _('Other')

    class SupportedForms(models.IntegerChoices):
        EIGHT = 8, _('8')
        NINTH = 9, _('9')
        TENTH = 10, _('10')
        ELEVENTH = 11, _('11')

    objects = UserManager()

    first_name = models.CharField(
        _('First name'), max_length=127, blank=False, null=False
    )
    last_name = models.CharField(
        _('Last name'), max_length=127, blank=False, null=False
    )
    patronymic_name = models.CharField(
        _('Patronymic name'), max_length=127, blank=True, null=False, default=''
    )
    gender = models.CharField(
        _('Gender'),
        max_length=1,
        blank=False,
        null=False,
        choices=GenderChoices.choices,
    )
    birth_date = models.DateField(_('Birth date'), null=False, blank=False)
    email = models.EmailField(_('Email'), null=False, blank=False, unique=True)
    phone = PhoneNumberField(_('Phone'), null=False, blank=False, unique=True)
    passport = models.CharField(
        _('Passport'),
        max_length=12,
        validators=[RegexValidator(r'(\d{4} \d{6})|(..-.. \d{6})')],
        unique=True,
        blank=False,
        null=False,
        help_text=_(
            'Passport in format xxxx xxxxxx or birth proof in format XX-XX xxxxxx'
        ),
    )
    city = models.CharField(_('City'), max_length=63, null=False, blank=False)
    school = models.CharField(_('School'), max_length=255, blank=False, null=False)
    actual_form = models.PositiveSmallIntegerField(
        _('Actual form'), choices=PossibleForms.choices
    )
    participation_form = models.PositiveSmallIntegerField(
        _('Participation form'), choices=SupportedForms.choices
    )
    vk_link = models.URLField(_('VK link'), blank=True, default='')
    telegram_nickname = models.CharField(
        _('Telegram nickname'), max_length=127, blank=True, default=''
    )
    venue_selected = models.ForeignKey(
        Venue, models.SET_NULL, null=True, verbose_name=_('Venue')
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Event(models.Model):
    title = models.CharField(_('Title'), max_length=127, blank=False, null=False)
    link = models.URLField(_('Link'), help_text=_('Link to news page etc.'))
    start = models.DateTimeField(_('Start'))
    description = models.TextField(_('Description'))

    def __str__(self):
        return self.title[:30]
