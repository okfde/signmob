from django.conf import settings


def site_meta(request):
    return {"SITE_NAME": settings.SITE_NAME}
