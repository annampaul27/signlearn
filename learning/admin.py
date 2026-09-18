from django.contrib import admin
from .models import Sign


@admin.register(Sign)
class SignAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "letter",
        "difficulty",
        "order",
    )

    list_filter = (
        "category",
        "difficulty",
    )

    search_fields = (
        "name",
        "letter",
    )

    ordering = (
        "category",
        "order",
    )