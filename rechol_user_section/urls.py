import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('master/admin/', admin.site.urls),
    path('master/django-ses/', include('django_ses.urls')),
    path('profile/', include('users.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='js-i18n'),
    path('__debug__/', include(debug_toolbar.urls)),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
