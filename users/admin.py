# ruff: noqa: ERA001, RUF003
from __future__ import annotations

from io import BytesIO

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.postgres.forms import SplitArrayField
from django.core.mail import EmailMessage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

import openpyxl
import tablib
from concurrency.admin import ConcurrentModelAdmin
from import_export.admin import ExportMixin, ImportExportMixin, ImportExportModelAdmin
from import_export.fields import Field
from import_export.formats.base_formats import XLSX
from import_export.resources import ModelResource

from .forms import MarkField
from .models import (
    Appellation,
    ConfigurationSingleton,
    Event,
    OfflineProblem,
    OfflineResult,
    OnlineAppellation,
    OnlineProblem,
    OnlineSubmission,
    User,
    Venue,
)

admin.site.register(ConfigurationSingleton)


class MyXLSX(XLSX):
    def create_dataset(self, in_stream):
        """Create dataset from first sheet, adding values for missing row cells."""
        # 'data_only' means values are read from formula cells, not the formula itself
        xlsx_book = openpyxl.load_workbook(
            BytesIO(in_stream),
            read_only=True,
            data_only=True,
        )

        dataset = tablib.Dataset()
        sheet = xlsx_book.active

        # obtain generator
        rows = sheet.rows
        dataset.headers = [cell.value for cell in next(rows)]
        xlen = len(dataset.headers)
        for row in rows:
            row_values = ([cell.value for cell in row] + [""] * xlen)[:xlen]
            dataset.append(row_values)

        return dataset


class VenueResource(ModelResource):
    class Meta:
        model = Venue


class EventResource(ModelResource):
    class Meta:
        model = Event


class UserResource(ModelResource):
    venue_selected = Field(attribute="venue_selected_id", column_name="venue_selected")

    class Meta:
        model = User
        raise_errors = True

        fields = export_order = (
            "first_name",
            "last_name",
            "patronymic_name",
            "gender",
            "birth_date",
            "email",
            "phone",
            "passport",
            "city",
            "school",
            "actual_form",
            "participation_form",
            "vk_link",
            "telegram_nickname",
            "venue_selected",
        )
        import_id_fields = ["email"]

    def dehydrate_venue_selected(self, instance):
        return str(instance.venue_selected)

    def dehydrate_actual_form(self, instance):
        form = instance.actual_form
        if form == 1:
            return "Other"
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
        (None, {"fields": ("password",)}),
        (_("Name"), {"fields": ("first_name", "last_name", "patronymic_name")}),
        (
            _("Private"),
            {"fields": ("gender", "birth_date", "passport", "school", "actual_form")},
        ),
        (_("Participant"), {"fields": ("participation_form", "venue_selected")}),
        (_("Contact"), {"fields": ("email", "phone", "city")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Name"), {"fields": ("first_name", "last_name", "patronymic_name")}),
    )

    list_display = (
        "last_name",
        "first_name",
        "participation_form",
        "patronymic_name",
        "city",
        "venue_selected",
        "email",
    )
    search_fields = ("email", "first_name", "last_name", "city", "participation_form")
    list_filter = ("role", "participation_form", "city", "venue_selected")
    ordering = ("participation_form", "last_name")
    actions = ["send_email"]

    @admin.action(description=_("Send email to selected users"))
    def send_email(self, request, queryset):
        file = request.FILES.get("attachment")
        if "subject" in request.POST:
            for user in queryset:
                try:
                    body = request.POST["template"].format(
                        name=f"{user.first_name} {user.last_name}",
                    )
                except ValueError:
                    self.message_user(
                        request,
                        "Invalid email template, please try again",
                        level=messages.ERROR,
                    )
                    return HttpResponseRedirect(request.get_full_path())

                msg = EmailMessage(
                    request.POST["subject"],
                    body,
                    f'"Проектная химическая олимпиада" <{settings.DEFAULT_FROM_EMAIL}>',
                    [user.email],
                )
                if file:
                    msg.attach(file.name, file.read())
                msg.send(fail_silently=False)

            self.message_user(request, f"Sent emails to {queryset.count()} users")
            return HttpResponseRedirect(request.get_full_path())

        return render(request, "admin/email_send.html", context={"users": queryset})

    def get_import_formats(self):
        return [f for f in super().get_import_formats() if not issubclass(f, XLSX)] + [
            MyXLSX,
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

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        not_required_fields = [
            "gender",
            "birth_date",
            "passport",
            "school",
            "actual_form",
            "participation_form",
            "phone",
            "city",
        ]
        for field_name in not_required_fields:
            if field := form.base_fields.get(field_name):
                field.required = False
        return form


USER_FIELDS = (
    "user__first_name",
    "user__last_name",
    "user__patronymic_name",
    "user__gender",
    "user__birth_date",
    "user__email",
    "user__phone",
    "user__passport",
    "user__city",
    "user__school",
    "user__actual_form",
    "user__participation_form",
    "user__vk_link",
    "user__telegram_nickname",
)


class _ResultResource(ModelResource):
    score1 = Field()
    score2 = Field()
    score3 = Field()
    score4 = Field()
    total = Field()

    def __getattr__(self, key):
        if key.startswith("dehydrate_score"):
            num = int(key[-1])

            def fn(instance):
                try:
                    return instance.final_scores[num - 1] or instance.scores[num - 1]
                except IndexError:
                    try:
                        return instance.scores[num - 1]
                    except IndexError:
                        return 0

            return fn

        return super().__getattr__(key)

    def dehydrate_total(self, instance):
        return instance.total_score

    def dehydrate_user__actual_form(self, instance):
        form = instance.user.actual_form
        if form == 1:
            return "Other"
        return form


class OfflineResultResource(_ResultResource):
    score5 = Field()
    score6 = Field()

    class Meta:
        model = OfflineResult
        raise_errors = True

        fields = export_order = (
            *USER_FIELDS,
            "user__venue_selected",
            "score1",
            "score2",
            "score3",
            "score4",
            "score5",
            "score6",
            "total",
        )


class OnlineSubmissionResource(_ResultResource):
    class Meta:
        model = OnlineSubmission
        raise_errors = True

        fields = export_order = (
            *USER_FIELDS,
            "score1",
            "score2",
            "score3",
            "score4",
            "total",
        )


class OfflineResultForm(forms.ModelForm):
    class Meta:
        model = OfflineResult
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scores"] = SplitArrayField(
            MarkField(required=False),
            size=6,
            required=False,
            initial=[],
        )
        self.fields["final_scores"] = SplitArrayField(
            MarkField(required=False),
            size=6,
            required=False,
            initial=[],
        )
        self.fields["version"].widget.attrs["readonly"] = True


class OnlineSubmissionForm(forms.ModelForm):
    class Meta:
        model = OnlineSubmission
        exclude = ("started",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scores"] = SplitArrayField(
            MarkField(required=False),
            size=4,
            required=False,
            initial=[],
        )
        self.fields["final_scores"] = SplitArrayField(
            MarkField(required=False),
            size=4,
            required=False,
            initial=[],
        )


class _ResultAdminMixin(ExportMixin):
    list_display = (
        "get_user__last_name",
        "get_user__first_name",
        "get_user__participation_form",
        "scores",
        "get_total",
    )
    search_fields = (
        "user__last_name",
        "user__first_name",
        "user__participation_form",
    )
    ordering = ("user__participation_form", "user__last_name", "user__first_name")

    def has_add_permission(self, request):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_module_permission(self, request):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_change_permission(self, request, _obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_delete_permission(self, request, _obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    def has_view_permission(self, request, _obj=None):
        return not request.user.is_anonymous and (
            request.user.is_superuser or request.user.role == User.Roles.JUDGE
        )

    @admin.display(ordering="user__last_name", description=_("Participant last name"))
    def get_user__last_name(self, obj):
        return obj.user.last_name

    @admin.display(ordering="user__first_name", description=_("Participant first name"))
    def get_user__first_name(self, obj):
        return obj.user.first_name

    @admin.display(
        ordering="user__participation_form",
        description=_("Participation form"),
    )
    def get_user__participation_form(self, obj):
        return obj.user.participation_form

    @admin.display(description=_("Total score"))
    def get_total(self, obj):
        return obj.total_score


@admin.register(OfflineResult)
class OfflineResultAdmin(_ResultAdminMixin, ConcurrentModelAdmin):
    resource_class = OfflineResultResource
    form = OfflineResultForm
    autocomplete_fields = ("user",)

    list_display = (*_ResultAdminMixin.list_display, "get_user__venue_selected")
    search_fields = (
        *_ResultAdminMixin.search_fields,
        "user__venue_selected__city",
        "user__venue_selected__name",
    )
    list_select_related = ("user",)
    list_filter = ("user__venue_selected", "user__participation_form")

    @admin.display(description=_("Venue"))
    def get_user__venue_selected(self, obj):
        return str(obj.user.venue_selected or "")


@admin.register(OnlineProblem)
class OnlineProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(OfflineProblem)
class OfflineProblemAdmin(admin.ModelAdmin):
    pass


@admin.register(OnlineSubmission)
class OnlineSubmissionAdmin(_ResultAdminMixin, admin.ModelAdmin):
    resource_class = OnlineSubmissionResource
    form = OnlineSubmissionForm
    autocomplete_fields = ("user",)
    change_list_template = "admin/users/onlinesubmission/change_list.html"

    list_display = (
        *_ResultAdminMixin.list_display,
        "was_submitted",
        "get_problem__name",
        "started",
    )
    search_fields = (*_ResultAdminMixin.search_fields, "problem__name")
    list_select_related = ("user", "problem")

    @admin.display(ordering="problem__name", description=_("Problem name"))
    def get_problem__name(self, obj):
        return obj.problem.name

    @admin.display(description=_("Was submitted?"))
    def was_submitted(self, obj):
        return bool(obj.file)

    def get_search_results(self, request, queryset, search_term):
        if only_gradeable := ("ONLY_GRADEABLE" in search_term):
            search_term = search_term.replace("ONLY_GRADEABLE", "").strip()

        qs, may_have_duplicates = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        if only_gradeable:
            qs = qs.exclude(Q(problem__name__startswith="Пробн") | Q(paper_original=""))
        return qs, may_have_duplicates


class AppellationBaseAdmin(ExportMixin, admin.ModelAdmin):
    list_display = (
        "get_result__user__last_name",
        "get_result__user__first_name",
        "get_result__user__participation_form",
        "message",
        "response",
        "when",
    )
    search_fields = (
        "result__user__first_name",
        "result__user__last_name",
        "result__user__participation_form",
    )
    ordering = ("when",)
    list_select_related = ("result", "result__user")

    @admin.display(
        ordering="result__user__last_name",
        description=_("Participant last name"),
    )
    def get_result__user__last_name(self, obj):
        return obj.result.user.last_name

    @admin.display(
        ordering="result__user__first_name",
        description=_("Participant first name"),
    )
    def get_result__user__first_name(self, obj):
        return obj.result.user.first_name

    @admin.display(
        ordering="result__user__participation_form",
        description=_("Participation form"),
    )
    def get_result__user__participation_form(self, obj):
        return obj.result.user.participation_form


class AppellationResource(ModelResource):
    class Meta:
        model = Appellation


@admin.register(Appellation)
class AppellationAdmin(AppellationBaseAdmin):
    resource_class = AppellationResource


class OnlineAppellationResource(ModelResource):
    class Meta:
        model = OnlineAppellation


@admin.register(OnlineAppellation)
class OnlineAppellationAdmin(AppellationBaseAdmin):
    resource_class = OnlineAppellationResource
