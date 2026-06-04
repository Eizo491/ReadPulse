from rest_framework import serializers
from .models import FavoriteBook, CommunityBook, BookRequest


class FavoriteBookSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FavoriteBook
        fields = [
            'id', 'user', 'google_books_id', 'title', 'authors',
            'description', 'thumbnail', 'published_date', 'page_count',
            'categories', 'average_rating', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class CommunityBookSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CommunityBook
        fields = [
            'id', 'owner', 'owner_username', 'title', 'authors',
            'description', 'thumbnail', 'published_date', 'page_count',
            'categories', 'isbn', 'publisher', 'language', 'google_books_id',
            'listing_type', 'condition', 'notes', 'contact_info', 'location',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'owner_username', 'created_at', 'updated_at']


class BookRequestSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    book_title = serializers.CharField(source='community_book.title', read_only=True)
    book_owner_username = serializers.CharField(source='community_book.owner.username', read_only=True)

    class Meta:
        model = BookRequest
        fields = [
            'id', 'community_book', 'book_title', 'book_owner_username',
            'requester', 'requester_username', 'request_type', 'message',
            'status', 'meetup_datetime', 'meetup_location',
            'swap_book_title', 'swap_book_authors', 'swap_book_thumbnail',
            'swap_book_condition', 'swap_book_description', 'swap_book_google_id',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'requester', 'requester_username',
            'book_title', 'book_owner_username', 'created_at', 'updated_at',
        ]
