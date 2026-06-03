from django.urls import path
from . import views

urlpatterns = [
    # ── Page routes ──
    path('', views.search_page, name='search'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('books/<str:google_books_id>/', views.book_detail_page, name='book_detail'),
    path('community/', views.community_page, name='community'),
    path('community/<int:book_id>/', views.community_book_detail_page, name='community_book_detail'),
    path('my-books/', views.my_books_page, name='my_books'),
    path('my-requests/', views.my_requests_page, name='my_requests'),
    path('requests/', views.requests_page, name='requests'),

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
    # IMPORTANT: all static/fixed paths MUST come before parameterised (<int:...>) ones
    path('api/community/add/', views.api_add_community_book, name='api_community_add'),
    path('api/community/all-requests/', views.api_list_all_requests, name='api_all_requests'),
    path('api/community/requests/<int:request_id>/status/', views.api_update_borrow_status, name='api_borrow_status'),
    path('api/community/requests/<int:request_id>/edit/', views.api_edit_borrow_request, name='api_borrow_edit'),
    path('api/community/requests/<int:request_id>/cancel/', views.api_cancel_borrow_request, name='api_borrow_cancel'),
    path('api/community/requests/<int:request_id>/', views.api_get_borrow_request, name='api_borrow_detail'),
    path('api/community/<int:book_id>/borrow/', views.api_request_borrow, name='api_community_borrow'),
    path('api/community/<int:book_id>/update/', views.api_update_community_book, name='api_community_update'),
    path('api/community/<int:book_id>/delete/', views.api_delete_community_book, name='api_community_delete'),
    path('api/community/<int:book_id>/', views.api_community_book_detail, name='api_community_detail'),
    path('api/community/', views.api_list_community_books, name='api_community_list'),

    # ── Session-backed My Books & My Requests ──
    path('api/session/my-books/', views.api_session_my_books, name='api_session_my_books_list'),
    path('api/session/my-books/add/', views.api_session_add_my_book, name='api_session_my_books_add'),
    path('api/session/my-books/<int:book_id>/remove/', views.api_session_remove_my_book, name='api_session_my_books_remove'),
    path('api/session/my-requests/', views.api_session_my_requests, name='api_session_my_requests_list'),
    path('api/session/my-requests/add/', views.api_session_add_my_request, name='api_session_my_requests_add'),
    path('api/session/my-requests/<int:request_id>/remove/', views.api_session_remove_my_request, name='api_session_my_requests_remove'),
]