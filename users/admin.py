# from datetime import datetime as dt
from io import BytesIO

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin, ImportExportModelAdmin
from import_export.fields import Field
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource

from .models import Event, User, Venue


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
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
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
    search_fields = ('email', 'first_name', 'last_name', 'city')
    ordering = ('participation_form', 'last_name')

    def get_import_formats(self):
        return [f for f in super().get_import_formats() if not issubclass(f, XLSX)] + [
            MyXLSX
        ]
