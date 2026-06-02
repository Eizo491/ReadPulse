from django.contrib import admin
from .models import FavoriteBook, CommunityBook, BorrowRequest


@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'published_date', 'created_at']
    search_fields = ['title', 'authors']


@admin.register(CommunityBook)
class CommunityBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'owner_name', 'location', 'condition', 'is_available', 'created_at']
    list_filter = ['condition', 'is_available']
    search_fields = ['title', 'authors', 'owner_name', 'location']


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ['requester_name', 'book', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['requester_name', 'book__title']
