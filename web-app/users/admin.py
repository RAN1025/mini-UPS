from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ('User ID', { 'fields': ('User_ID',)}),)

    list_display = ['username','User_ID']

admin.site.register(CustomUser, CustomUserAdmin)
