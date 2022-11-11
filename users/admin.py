from io import BytesIO

from concurrency.admin import ConcurrentModelAdmin
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.postgres.forms import SplitArrayField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from import_export.admin import ExportMixin, ImportExportMixin, ImportExportModelAdmin
from import_export.fields import Field
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource

from .models import (
    Appellation,
    Event,
    OfflineResult,
    OnlineProblem,
    OnlineSubmission,
    User,
    Venue,
)


class MyXLSX(XLSX):
    def create_dataset(self, in_stream):
        """Create dataset from first sheet, adding values for missing row cells."""

        import openpyxl
        import tablib

        # 'data_only' means values are read from formula cells, not the formula itself
        xlsx_book = openpyxl.load_workbook(
            BytesIO(in_stream), read_only=True, data_only=True
        )

        dataset = tablib.Dataset()
        sheet = xlsx_book.active

        # obtain generator
        rows = sheet.rows
        dataset.headers = [cell.value for cell in next(rows)]
        xlen = len(dataset.headers)
        for row in rows:
            row_values = ([cell.value for cell in row] + [''] * xlen)[:xlen]
            dataset.append(row_values)

        return dataset


class VenueResource(ModelResource):
    class Meta:
        model = Venue


class EventResource(ModelResource):
    class Meta:
        model = Event


class UserResource(ModelResource):
    # These commented out fields were used to import.
    # Perhaps we'll need it again, so not removing.
    # The same holds for commented out methods

    # first_name = Field(attribute='first_name', column_name='surname')
    # last_name = Field(attribute='last_name', column_name='name')
    # patronymic_name = Field(
    #     attribute='patronymic_name', column_name='patronymic_name'
    # )
    # gender = Field(attribute='gender', column_name='sex')
    # birth_date = Field(attribute='birth_date', column_name='birth_date')
    # email = Field(attribute='email', column_name='email')
    # phone = Field(attribute='phone', column_name='phone')
    # passport = Field(attribute='passport', column_name='passport')
    # city = Field(attribute='city', column_name='city')
    # school = Field(attribute='school', column_name='school')
    # actual_form = Field(attribute='actual_form', column_name='class')
    # participation_form = Field(attribute='participation_form', column_name='gr')
    # vk_link = Field(attribute='vk_link', column_name='vk_page')
    # telegram_nickname = Field(attribute='telegram_nickname', column_name='')
    # WTF why is it in Russian...
    # venue_selected = Field(
    #     attribute='venue_selected_id', column_name='Площадка_проведения'
    # )

    venue_selected = Field(attribute='venue_selected_id', column_name='venue_selected')

    class Meta:
        model = User
        raise_errors = True

        fields = export_order = (
            'first_name',
            'last_name',
            'patronymic_name',
            'gender',
            'birth_date',
            'email',
            'phone',
            'passport',
            'city',
            'school',
            'actual_form',
            'participation_form',
            'vk_link',
            'telegram_nickname',
            'venue_selected',
        )
        import_id_fields = ['email']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.passport_cache = set()
    #     self.email_cache = set()
    #     self.phone_cache = set()

    # def import_field(self, field, obj, data, is_m2m=False, **kwargs):
    #     ids = {
    #         'Москва, Школа ЦПМ': 1,
    #         'Москва, ГБОУ Школа ЦПМ': 1,
    #         'Санкт-Петербург, МБОУ СОШ Калининского района': 2,
    #         'Калининград, ГБОУ Школа № 1560 «Лидер»': 3,
    #         'Ставропольский край, г. Новоалександровск, МОУ СОШ №12': 4,
    #         'Москва, ГБОУ Школа № 1560 «Лидер»': 5,
    #         'Уфа, ГБОУ РИЛИ': 6,
    #         'Краснодар, АНОО Пушкинская школа': 7,
    #         'Приморский край, пос. Новый, МБОУ СОШ 6': 8,
    #         'Амурская область, г. Свободный, МОАУ гимназия №9': 9,
    #         'Архангельская область, г. Котлас, МОУ СОШ №7': 10,
    #         'Волгоград, НОУ СО Частная интегрированная школа': 11,
    #         'Людиново, МКОУ Средняя школа 4': 12,
    #         'Кемерово, ГБНОУ ГМЛИ': 13,
    #         'Кострома, МБОУ СОШ №21': 14,
    #         'Коломна, МБОУ Гимназия №8': 15,
    #         'Реутов , МАОУ СОШ 10': 16,
    #         'Дзержинск, МБОУ школа №27': 17,
    #         'Оренбург, МОАУ Гимназия 1': 18,
    #         'Свердловская область, г. Алапаевск, МАОУ СОШ №1': 19,
    #         'Первоуральск, МАОУ СОШ 7 с углубленным изучением отдельных предметов': 20,  # noqa
    #         'Челябинск, ФГБОУ ВО Южно-Уральский государственный гуманитарно-педагогический университет': 21,  # noqa
    #         # !!! 22 is missing
    #         'Казань, МАОУ Лицей №131': 23,
    #         'Екатеринбург, СУНЦ УрФУ': 24,
    #         'ХМАО-Югра, г. Урай, МБОУ СОШ 12': 25,
    #         'Реж, МАОУ «Средняя общеобразовательная школа № 44»': 26,
    #         'Нижний Новгород, Центр дополнительного и инновационного образования Медумники при ФГБОУ ВО ПИМУ': 27,  # noqa
    #         'Киров, КОГАОУ ДО ЦДООШ': 28,
    #         'Москва, ГБОУ Школа № 199': 29,
    #         'Пермь, МАОУ СОШ37': 30,
    #         'Татарск, МБОУ-ЛИЦЕЙ': 31,
    #         'Москва, ГБОУ Школа №709': 32,
    #         'Калуга, МБОУ СОШ 15': 33,
    #         'Пермь, МАОУ Средняя общеобразовательная школа Петролеум+': 34,
    #         'пгт Новый Торъял, МБОУ Новоторьяльская СОШ': 35,
    #         'Республика Марий Эл, пгт Новый Торъял, МБОУ  Новоторьяльская СОШ': 35,
    #         'Волгоград, ФГБОУ ВО Волгоградский государственный аграрный университет': 36,  # noqa
    #         'Тюмень, Тюменский ГМУ': 37,
    #     }
    #     genders = {
    #         'Муж.': 'm',
    #         'Жен.': 'f',
    #     }

    #     fancy = data[field.column_name]
    #     if field.attribute == 'venue_selected_id':
    #         data[field.column_name] = ids[fancy]
    #     elif field.attribute == 'birth_date':
    #         data[field.column_name] = dt.strptime(fancy, '%d.%m.%Y').date()
    #     elif field.attribute == 'gender':
    #         data[field.column_name] = genders[fancy]
    #     elif field.attribute == 'actual_form':
    #         data[field.column_name] = 1 if fancy == 'Другое' else fancy

    #     return super().import_field(field, obj, data, is_m2m=False, **kwargs)

    # def skip_row(self, instance, original):
    #     if instance.passport in self.passport_cache:
    #         return True
    #     if instance.email in self.email_cache:
    #         return True
    #     if instance.phone in self.phone_cache:
    #         return True

    #     self.passport_cache.add(instance.passport)
    #     self.email_cache.add(instance.email)
    #     self.phone_cache.add(instance.phone)
    #     return super().skip_row(instance, original)

    def dehydrate_venue_selected(self, instance):
        return str(instance.venue_selected)

    def dehydrate_actual_form(self, instance):
        form = instance.actual_form
        if form == 1:
            return 'Other'
        return form


@admin.register(Venue)
class VenueAdmin(ImportExportModelAdmin):
    resource_class = VenueResource


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource


@admin.register(User)
class UserAdmin(ImportExportMixin, DjangoUserAdmin):
    resource_class = UserResource

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
        (None, {'fields': ('email', 'password')}),
        (_('Name'), {'fields': ('first_name', 'last_name', 'patronymic_name')}),
    )

    list_display = (
        'last_name',
        'first_name',
        'participation_form',
        'patronymic_name',
        'city',
        'venue_selected',
        'email',
    )
    search_fields = ('email', 'first_name', 'last_name', 'city', 'participation_form')
    ordering = ('participation_form', 'last_name')

    def get_import_formats(self):
        return [f for f in super().get_import_formats() if not issubclass(f, XLSX)] + [
            MyXLSX
        ]

    def has_module_permission(self, request):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_view_permission(self, request, obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser
            or request.user.role == User.Roles.JUDGE
            and (not obj or obj.role == User.Roles.PARTICIPANT)
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(role=User.Roles.PARTICIPANT)

    def get_search_results(self, request, queryset, search_term):
        qs, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        if request.user.is_superuser:
            return qs, may_have_duplicates
        qs = qs.filter(role=User.Roles.PARTICIPANT)
        return qs, may_have_duplicates


class OfflineResultResource:
    class Meta:
        model = OfflineResult


class MarkField(forms.CharField):
    def validate(self, value):
        if not value or value == '-':
            return
        super().validate(value)
        try:
            float(value)
        except ValueError:
            raise ValidationError(
                _('Not a valid integer or hyphen.'), code='INVALID_INTEGER'
            )


class OfflineResultForm(forms.ModelForm):
    class Meta:
        model = OfflineResult
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scores'] = SplitArrayField(
            MarkField(required=False), size=6, required=False, initial=[]
        )
        self.fields['final_scores'] = SplitArrayField(
            MarkField(required=False), size=6, required=False, initial=[]
        )
        self.fields['version'].widget.attrs['readonly'] = True


@admin.register(OfflineResult)
class OfflineResultAdmin(ExportMixin, ConcurrentModelAdmin):
    resource_class = OfflineResultResource
    autocomplete_fields = ('user',)
    form = OfflineResultForm

    list_display = (
        'get_user__last_name',
        'get_user__first_name',
        'get_user__participation_form',
        'scores',
        'get_total',
        'get_user__venue_selected',
    )
    search_fields = (
        'user__last_name',
        'user__first_name',
        'user__participation_form',
        'user__venue_selected__city',
        'user__venue_selected__name',
    )
    ordering = ('user__participation_form', 'user__last_name')

    def has_add_permission(self, request):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_module_permission(self, request):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_change_permission(self, request, obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_delete_permission(self, request, obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_view_permission(self, request, obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    @admin.display(ordering='user__last_name', description=_('Participant last name'))
    def get_user__last_name(self, obj):
        return obj.user.last_name

    @admin.display(ordering='user__first_name', description=_('Participant first name'))
    def get_user__first_name(self, obj):
        return obj.user.first_name

    @admin.display(
        ordering='user__participation_form', description=_('Participation form')
    )
    def get_user__participation_form(self, obj):
        return obj.user.participation_form

    @admin.display(description=_('Total score'))
    def get_total(self, obj):
        return sum(float(x) if x and x != '-' else 0 for x in obj.scores)

    @admin.display(description=_('Venue'))
    def get_user__venue_selected(self, obj):
        return str(obj.user.venue_selected or '')


@admin.register(OnlineProblem)
class OnlineProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(OnlineSubmission)
class OnlineSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'get_user__last_name',
        'get_user__first_name',
        'get_user__participation_form',
        'get_problem__name',
        'started',
        'file',
    )
    search_fields = ('user__first_name', 'user__last_name', 'problem__name')
    ordering = ('user__participation_form', 'user__last_name', 'user__first_name')

    @admin.display(ordering='user__last_name', description=_('Participant last name'))
    def get_user__last_name(self, obj):
        return obj.user.last_name

    @admin.display(ordering='user__first_name', description=_('Participant first name'))
    def get_user__first_name(self, obj):
        return obj.user.first_name

    @admin.display(ordering='problem__name', description=_('Problem name'))
    def get_problem__name(self, obj):
        return obj.problem.name

    @admin.display(
        ordering='user__participation_form', description=_('Participation form')
    )
    def get_user__participation_form(self, obj):
        return obj.user.participation_form


class AppellationResource(ModelResource):
    class Meta:
        model = Appellation


# class OfflineResultInline(admin.StackedInline):
#     model = OfflineResult
#     extra = 0


@admin.register(Appellation)
class AppellationAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AppellationResource
    list_display = (
        'get_result__user__last_name',
        'get_result__user__first_name',
        'get_result__user__participation_form',
        'message',
        'response',
        'when',
    )
    search_fields = (
        'result__user__first_name',
        'result__user__last_name',
        'result__user__participation_form',
    )
    ordering = ('when',)
    list_select_related = ('result', 'result__user')
    # inlines = [OfflineResultInline]

    @admin.display(
        ordering='result__user__last_name', description=_('Participant last name')
    )
    def get_result__user__last_name(self, obj):
        return obj.result.user.last_name

    @admin.display(
        ordering='result__user__first_name', description=_('Participant first name')
    )
    def get_result__user__first_name(self, obj):
        return obj.result.user.first_name

    @admin.display(
        ordering='result__user__participation_form', description=_('Participation form')
    )
    def get_result__user__participation_form(self, obj):
        return obj.result.user.participation_form
