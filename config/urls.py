from django.conf import settings
from django.urls import include, path, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from django.views.generic import TemplateView
from django.views.decorators.clickjacking import xframe_options_exempt

from rest_framework.routers import DefaultRouter

from signmob.collection.api_views import CollectionViewSet
from signmob.users.views import link_login
from signmob.views import ContactView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"collection", CollectionViewSet, basename="collection")

urlpatterns = [
    path("", include("signmob.collection.urls", namespace="collection")),

    path("termine/", include('signmob.calendar_urls', namespace='schedule')),
    path("termine/", include("schedule.urls")),
    path("api/", include(router.urls)),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("signmob.users.urls", namespace="user")),
    re_path(
        r'^go/(?P<user_id>\d+)/(?P<secret>\w{32})(?P<url>/.*)$',
        link_login, name='link_login'
    ),
    path("accounts/", include("allauth.urls")),
    path(
        'kontakt/',
        xframe_options_exempt(ContactView.as_view()),
        name='contact'
    ),
    path(
        'kontakt/danke/',
        xframe_options_exempt(TemplateView.as_view(
            template_name='contact_thanks.html'
        )),
        name='contact-thanks'
    ),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
