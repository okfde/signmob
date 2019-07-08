from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from signmob.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


fieldsets = auth_admin.UserAdmin.fieldsets


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]

    fieldsets = [
        ("User", {"fields": ("name", "email")}),
        (None, {"fields": ("username", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    ]
