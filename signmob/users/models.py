import hashlib
import hmac

from django.db import models
from django.contrib.gis.db import models as geo_models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.crypto import constant_time_compare


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        return self._create_user(
            email, username, password, False, False, **extra_fields
        )

    def create_superuser(self, email, username, password=None, **extra_fields):
        return self._create_user(email, username, password, True, True, **extra_fields)

    def _create_user(
        self, email, username, password, is_staff, is_superuser, **extra_fields
    ):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)

        username = ''
        if username:
            username = self.model.normalize_username(username)

        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=None,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        help_text=_(
            "150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={"unique": _("A user with that username already exists.")},
    )
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    mobile = models.CharField(_('Phone number'), blank=True, max_length=255)
    geo = geo_models.PointField(null=True, blank=True, geography=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    date_deactivated = models.DateTimeField(
        _("date deactivated"), default=None, null=True, blank=True
    )
    is_deleted = models.BooleanField(
        _("deleted"),
        default=False,
        help_text=_("Designates whether this user was deleted."),
    )
    date_left = models.DateTimeField(
        _("date left"), default=None, null=True, blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.name

    def get_autologin_url(self, url):
        return settings.SITE_URL + reverse('account-go', kwargs={
            "user_id": self.id,
            "secret": self.generate_autologin_secret(),
            "url": url
        })

    def check_autologin_secret(self, secret):
        return constant_time_compare(self.generate_autologin_secret(), secret)

    def generate_autologin_secret(self):
        to_sign = [str(self.pk)]
        if self.last_login:
            to_sign.append(self.last_login.strftime("%Y-%m-%dT%H:%M:%S"))
        return hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            (".".join(to_sign)).encode('utf-8'),
            digestmod=hashlib.md5
        ).hexdigest()

    def send_mail(self, subject, body, **kwargs):
        from .utils import send_mail_user
        return send_mail_user(subject, body, self, **kwargs)
