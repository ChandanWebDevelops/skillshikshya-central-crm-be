from django.contrib import admin
from apps.account.models import OTP, User


class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'designation', 'is_active', 'is_staff']
    search_fields = ['name', 'email']


admin.site.register(User, UserAdmin)


class OTPAdmin(admin.ModelAdmin):
    list_display = ['email', 'otp', 'is_verified', 'created_at']
    list_filter = ['is_verified']
    search_fields = ['email']


admin.site.register(OTP, OTPAdmin)
