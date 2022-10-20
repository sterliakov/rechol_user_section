from concurrency.fields import IntegerVersionField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as UserManager_
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Venue(models.Model):
    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')

    city = models.CharField(_('City'), max_length=63, blank=False, null=False)
    name = models.CharField(_('Name'), max_length=63, blank=False, null=False)
    full_address = models.CharField(
        _('Address'), max_length=255, blank=False, null=False
    )

    def __str__(self):
        return f'{self.name} ({self.city}, {self.full_address})'


class UserManager(UserManager_):
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
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

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

    class Roles(models.TextChoices):
        PARTICIPANT = 'p', _('Participant')
        ADMIN = 'a', _('Admin')
        JUDGE = 'j', _('Judge')

    objects = UserManager()
    email = models.EmailField(_('Email'), null=False, blank=False, unique=True)

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
    birth_date = models.DateField(_('Birth date'), null=True, blank=False)
    phone = PhoneNumberField(_('Phone'), null=True, blank=False, unique=True)
    passport = models.CharField(  # noqa
        _('Passport'),
        max_length=15,
        validators=[MinLengthValidator(9)],
        unique=True,
        blank=False,
        null=True,
        help_text=_(
            'Passport in format xxxx xxxxxx or birth proof in format XX-XX xxxxxx'
        ),
    )
    city = models.CharField(_('City'), max_length=63, null=True, blank=False)  # noqa
    school = models.CharField(  # noqa
        _('School'), max_length=255, blank=False, null=True
    )
    actual_form = models.PositiveSmallIntegerField(
        _('Actual form'), choices=PossibleForms.choices, null=True
    )
    participation_form = models.PositiveSmallIntegerField(
        _('Participation form'), choices=SupportedForms.choices, null=True
    )
    vk_link = models.URLField(_('VK link'), blank=True, default='')
    telegram_nickname = models.CharField(
        _('Telegram nickname'), max_length=127, blank=True, default=''
    )
    venue_selected = models.ForeignKey(
        Venue, models.SET_NULL, blank=True, null=True, verbose_name=_('Venue')
    )
    online_selected = models.BooleanField(_('Online stage'), default=True, null=False)
    role = models.CharField(
        _('Role'),
        max_length=1,
        editable=False,
        choices=Roles.choices,
        blank=False,
        default=Roles.PARTICIPANT,
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, **kwargs):
        self.username = self.email
        return super().save(**kwargs)


class Event(models.Model):
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    title = models.CharField(_('Title'), max_length=127, blank=False, null=False)
    link = models.URLField(_('Link'), help_text=_('Link to news page etc.'))
    start = models.DateTimeField(_('Start'), null=True)
    description = models.TextField(_('Description'))

    def __str__(self):
        return self.title[:30]


class OfflineResult(models.Model):
    class Meta:
        verbose_name = _('Result (offline)')
        verbose_name_plural = _('Results (offline)')

    user = models.OneToOneField(User, models.CASCADE, verbose_name=_('Participant'))
    scores = ArrayField(
        models.CharField(max_length=2, default='', blank=True, null=False),
        size=5,
        verbose_name=_('Scores'),
        blank=True,
        default=list,
    )
    comment = models.TextField(_('Comment'), default='', blank=True, null=False)
    paper_original = models.FileField(_('Original work'), upload_to='originals')
    version = IntegerVersionField()

    def __str__(self):
        return f'Offline: {self.user}'


class Annotation(models.Model):
    class Meta:
        verbose_name = _('Annotation')
        verbose_name_plural = _('Annotations')

    filename = models.CharField(_('Filename'), max_length=255, blank=False, null=False)
    annotation_id = models.UUIDField(
        _('Annotation ID'), blank=False, null=False, primary_key=True
    )
    page = models.PositiveSmallIntegerField(_('Page number'), blank=False, null=False)
    annotation = models.TextField(_('Annotation content'), blank=False, null=False)

    def __str__(self):
        return f'{self.filename} ({self.annotation_id})'
