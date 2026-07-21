from django.contrib import admin
from apps.branch.models import Branch


class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']


admin.site.register(Branch, BranchAdmin)
