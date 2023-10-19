from django.contrib import admin

from .models import Paper


@admin.register(Paper)
class UserAdmin(admin.ModelAdmin):
    list_display = ["project_id", "title", "create_time", "update_time"]
    search_fields = ["project_id", "title"]
    date_hierarchy = "create_time"
    ordering = ["-create_time"]
    list_per_page = 10
