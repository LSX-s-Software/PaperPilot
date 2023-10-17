from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "phone", "create_time"]
    search_fields = ["username", "phone"]
    date_hierarchy = "create_time"
    ordering = ["-create_time"]
    fields = ["username", "phone", "avatar"]
    list_per_page = 10
