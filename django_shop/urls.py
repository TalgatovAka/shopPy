from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("set-language/", set_language, name="set-language"),
    path("oidc/", include("mozilla_django_oidc.urls")),
]

urlpatterns += i18n_patterns(
    path("", include("shop.urls", namespace="shop")),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
