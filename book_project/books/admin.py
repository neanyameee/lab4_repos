from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year', 'janr', 'created_at']
    list_filter = ['janr', 'year', 'created_at']
    search_fields = ['title', 'author', 'janr']
    ordering = ['-created_at']