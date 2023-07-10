from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import MyUsers, OtpModel


admin.site.register(OtpModel)


class NewUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("email", "phone_number", "is_admin")
    list_filter = ("is_admin",)

    fieldsets = (
        (None, {"fields": ("phone_number", "email", "full_name", "password")}),
        ('permisons', {"fields": ("is_admin", "is_active", "last_login")}),
    )
    add_fieldsets = (
        (None, {"fields": ("email", "full_name", "phone_number",  "password1", "password2")}),
    )
    search_fields = ("email", "full_name")
    filter_horizontal = ()
    ordering = ("full_name",)


admin.site.unregister(Group)
admin.site.register(MyUsers, NewUserAdmin)
