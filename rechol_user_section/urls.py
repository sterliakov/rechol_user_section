import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from users.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('master/admin/', admin.site.urls),
    path('master/django-ses/', include('django_ses.urls')),
    path('profile/', include('users.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='js-i18n'),
    path('__debug__/', include(debug_toolbar.urls)),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
