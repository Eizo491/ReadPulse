from django.urls import path
from . import views

urlpatterns = [
    # Page routes
    path('', views.search_page, name='search'),
    path('favorites/', views.favorites_page, name='favorites'),

    # RESTful API routes
    path('api/search/', views.api_search_books, name='api_search'),
    path('api/favorites/', views.api_list_favorites, name='api_favorites_list'),
    path('api/favorites/add/', views.api_add_favorite, name='api_favorites_add'),
    path('api/favorites/<str:google_books_id>/', views.api_favorite_detail, name='api_favorite_detail'),
    path('api/favorites/<str:google_books_id>/remove/', views.api_remove_favorite, name='api_favorite_remove'),
]
