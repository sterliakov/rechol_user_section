from __future__ import annotations

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

import debug_toolbar

from users.views import IndexView

i18n_paths = [
    path("master/admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("profile/", include("users.urls")),
]

urlpatterns = [
    path("master/django-ses/", include("django_ses.urls")),
    *i18n_patterns(*i18n_paths, prefix_default_language=False),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="js-i18n"),
    path("__debug__/", include(debug_toolbar.urls)),
    path("i18n/", include("django.conf.urls.i18n")),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
