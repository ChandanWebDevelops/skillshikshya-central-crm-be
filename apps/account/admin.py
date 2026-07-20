from django.contrib import admin
from apps.account.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'designation', 'is_active', 'is_staff']
    search_fields = ['name', 'email']


admin.site.register(User, UserAdmin)
