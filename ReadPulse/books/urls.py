from django.urls import path
from . import views

urlpatterns = [
    # ── Page routes ──
    path('', views.search_page, name='search'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('community/', views.community_page, name='community'),
    path('my-listings/', views.my_listings_page, name='my_listings'),
    path('requests/', views.requests_page, name='requests'),
    path('books/<str:google_books_id>/', views.book_detail_page, name='book_detail'),

    # ── RESTful API: Google Books ──
    path('api/search/', views.api_search_books, name='api_search'),
    path('api/search-audiobooks/', views.api_search_audiobooks, name='api_search_audiobooks'),
    path('api/popular-audiobooks/', views.api_popular_audiobooks, name='api_popular_audiobooks'),
    path('api/audiobook-rss/', views.api_audiobook_rss_proxy, name='api_audiobook_rss'),
    path('api/books/<str:google_books_id>/', views.api_book_detail, name='api_book_detail'),

    # ── RESTful API: Favorites ──
    path('api/favorites/', views.api_list_favorites, name='api_favorites_list'),
    path('api/favorites/add/', views.api_add_favorite, name='api_favorites_add'),
    path('api/favorites/<str:google_books_id>/remove/', views.api_remove_favorite, name='api_favorite_remove'),
    path('api/favorites/<str:google_books_id>/', views.api_favorite_detail, name='api_favorite_detail'),

    # ── RESTful API: Audiobook Favorites ──
    path('api/favorite-audiobooks/', views.api_list_favorite_audiobooks, name='api_fav_audiobooks_list'),
    path('api/favorite-audiobooks/add/', views.api_add_favorite_audiobook, name='api_fav_audiobooks_add'),
    path('api/favorite-audiobooks/<str:librivox_id>/remove/', views.api_remove_favorite_audiobook, name='api_fav_audiobook_remove'),
    path('api/favorite-audiobooks/<str:librivox_id>/', views.api_favorite_audiobook_detail, name='api_fav_audiobook_detail'),

    # ── RESTful API: Community Books ──
    path('api/community/', views.api_community_books, name='api_community_books'),
    path('api/community/add/', views.api_add_community_book, name='api_add_community_book'),
    path('api/community/my-listings/', views.api_my_listings, name='api_my_listings'),
    path('api/community/my-available-listings/', views.api_my_available_listings, name='api_my_available_listings'),
    path('api/community/<int:book_id>/', views.api_community_book_detail, name='api_community_book_detail'),

    # ── RESTful API: Book Requests ──
    path('api/requests/create/', views.api_create_request, name='api_create_request'),
    path('api/requests/mine/', views.api_my_requests, name='api_my_requests'),
    path('api/requests/for-me/', views.api_requests_for_me, name='api_requests_for_me'),
    path('api/requests/<int:request_id>/', views.api_update_request, name='api_update_request'),
]
