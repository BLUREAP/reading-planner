from django.contrib import admin
from .models import Book, ReadingPlan, ReadingSession


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'total_pages', 'deadline', 'user']
    list_filter = ['user', 'deadline']
    search_fields = ['title', 'author']


@admin.register(ReadingPlan)
class ReadingPlanAdmin(admin.ModelAdmin):
    list_display = ['book', 'start_date', 'daily_target', 'is_active']
    list_filter = ['is_active']


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    list_display = ['book', 'date', 'pages_read']
    list_filter = ['date']