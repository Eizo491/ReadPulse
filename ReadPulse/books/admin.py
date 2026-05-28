from django.contrib import admin
from .models import FavoriteBook

@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'published_date', 'created_at']
    search_fields = ['title', 'authors']
