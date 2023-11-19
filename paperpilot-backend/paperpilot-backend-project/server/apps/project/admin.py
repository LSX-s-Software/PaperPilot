from django.contrib import admin

from .models import Project, UserProject


@admin.register(Project)
class UserAdmin(admin.ModelAdmin):
    list_display = ["name", "invite_code", "create_time", "update_time"]
    search_fields = ["name", "invite_code"]
    date_hierarchy = "create_time"
    ordering = ["-create_time"]
    list_per_page = 10


@admin.register(UserProject)
class UserProjectAdmin(admin.ModelAdmin):
    list_display = ["user_id", "project", "is_owner", "create_time"]
    search_fields = ["user_id", "project"]
    date_hierarchy = "create_time"
    ordering = ["-create_time"]
    list_per_page = 10
