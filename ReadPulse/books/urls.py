from django.urls import path
from . import views

urlpatterns = [
    # ── Page routes ──
    path('', views.search_page, name='search'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('books/<str:google_books_id>/', views.book_detail_page, name='book_detail'),
    path('community/', views.community_page, name='community'),
    path('community/<int:book_id>/', views.community_book_detail_page, name='community_book_detail'),

    # ── RESTful API: Google Books ──
    path('api/search/', views.api_search_books, name='api_search'),
    path('api/search-audiobooks/', views.api_search_audiobooks, name='api_search_audiobooks'),
    path('api/books/<str:google_books_id>/', views.api_book_detail, name='api_book_detail'),

    # ── RESTful API: Favorites ──
    path('api/favorites/', views.api_list_favorites, name='api_favorites_list'),
    path('api/favorites/add/', views.api_add_favorite, name='api_favorites_add'),
    path('api/favorites/<str:google_books_id>/remove/', views.api_remove_favorite, name='api_favorite_remove'),
    path('api/favorites/<str:google_books_id>/', views.api_favorite_detail, name='api_favorite_detail'),

    # ── RESTful API: Community Books ──
    # IMPORTANT: static paths must come before parameterised ones
    path('api/community/add/', views.api_add_community_book, name='api_community_add'),
    path('api/community/requests/<int:request_id>/status/', views.api_update_borrow_status, name='api_borrow_status'),
    path('api/community/<int:book_id>/borrow/', views.api_request_borrow, name='api_community_borrow'),
    path('api/community/<int:book_id>/update/', views.api_update_community_book, name='api_community_update'),
    path('api/community/<int:book_id>/delete/', views.api_delete_community_book, name='api_community_delete'),
    path('api/community/<int:book_id>/', views.api_community_book_detail, name='api_community_detail'),
    path('api/community/', views.api_list_community_books, name='api_community_list'),

    # ── My Books page ──
    path('my-books/', views.my_books_page, name='my_books'),

    # ── Requests page ──
    path('requests/', views.requests_page, name='requests'),
    path('api/community/all-requests/', views.api_list_all_requests, name='api_all_requests'),
]
