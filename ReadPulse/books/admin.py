from django.contrib import admin
from .models import FavoriteBook, CommunityBook, BookRequest


@admin.register(FavoriteBook)
class FavoriteBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'created_at']
    search_fields = ['title', 'authors']


@admin.register(CommunityBook)
class CommunityBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'owner', 'listing_type', 'status', 'created_at']
    list_filter = ['listing_type', 'status']
    search_fields = ['title', 'authors', 'owner__username']


@admin.register(BookRequest)
class BookRequestAdmin(admin.ModelAdmin):
    list_display = ['community_book', 'requester', 'request_type', 'status', 'created_at']
    list_filter = ['request_type', 'status']
    search_fields = ['community_book__title', 'requester__username']
