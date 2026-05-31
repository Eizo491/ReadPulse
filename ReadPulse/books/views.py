import json
import urllib.request
import urllib.parse
import urllib.error

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import FavoriteBook


# ─────────────────────────────────────────────
# Page views
# ─────────────────────────────────────────────

def search_page(request):
    """Render the Search Books page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/search.html', {'fav_count': fav_count})


def book_detail_page(request, google_books_id):
    """Render the Book Detail page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/book_detail.html', {
        'google_books_id': google_books_id,
        'fav_count': fav_count,
    })


def favorites_page(request):
    """Render the Favorites page."""
    favorites = FavoriteBook.objects.all()
    return render(request, 'books/favorites.html', {
        'favorites': favorites,
        'fav_count': favorites.count(),
    })


# ─────────────────────────────────────────────
# RESTful API  –  /api/...
# ─────────────────────────────────────────────

@require_http_methods(["GET"])
def api_book_detail(request, google_books_id):
    """
    GET /api/books/<google_books_id>/ – fetch a single book's full details from Google Books API.
    """
    api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '').strip()
    if not api_key:
        return JsonResponse({'error': 'Google Books API key is not configured on the server.'}, status=500)

    url = f'https://www.googleapis.com/books/v1/volumes/{urllib.parse.quote(google_books_id)}?key={api_key}'

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            item = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            err_json = json.loads(body)
            msg = err_json.get('error', {}).get('message', str(e))
        except Exception:
            msg = str(e)
        return JsonResponse({'error': msg}, status=e.code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    info = item.get('volumeInfo', {})
    sale_info = item.get('saleInfo', {})
    image_links = info.get('imageLinks', {})

    # Prefer largest available image
    thumbnail = (
        image_links.get('extraLarge', '')
        or image_links.get('large', '')
        or image_links.get('medium', '')
        or image_links.get('small', '')
        or image_links.get('thumbnail', '')
        or image_links.get('smallThumbnail', '')
    )
    if thumbnail.startswith('http://'):
        thumbnail = thumbnail.replace('http://', 'https://', 1)

    favorite_ids = set(FavoriteBook.objects.values_list('google_books_id', flat=True))

    book = {
        'google_books_id': google_books_id,
        'title': info.get('title', 'Unknown Title'),
        'subtitle': info.get('subtitle', ''),
        'authors': ', '.join(info.get('authors', [])),
        'description': info.get('description', ''),
        'thumbnail': thumbnail,
        'published_date': info.get('publishedDate', ''),
        'page_count': info.get('pageCount'),
        'categories': ', '.join(info.get('categories', [])),
        'average_rating': info.get('averageRating'),
        'ratings_count': info.get('ratingsCount'),
        'language': info.get('language', ''),
        'publisher': info.get('publisher', ''),
        'isbn': next(
            (id_['identifier'] for id_ in info.get('industryIdentifiers', []) if id_['type'] == 'ISBN_13'),
            next((id_['identifier'] for id_ in info.get('industryIdentifiers', [])), '')
        ),
        'preview_link': info.get('previewLink', ''),
        'info_link': info.get('infoLink', ''),
        'buy_link': sale_info.get('buyLink', ''),
        'is_favorite': google_books_id in favorite_ids,
    }

    return JsonResponse({'book': book})


@require_http_methods(["GET"])
def api_search_books(request):
    """
    GET /api/search/?q=<query>&max_results=<n>&start_index=<n>
    Proxy the Google Books API and return JSON.
    API key is read from settings.GOOGLE_BOOKS_API_KEY.
    """
    query = request.GET.get('q', '').strip()
    max_results = request.GET.get('max_results', '20')
    start_index = request.GET.get('start_index', '0')
    api_key = getattr(settings, 'GOOGLE_BOOKS_API_KEY', '').strip()

    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required.'}, status=400)
    if not api_key:
        return JsonResponse({'error': 'Google Books API key is not configured on the server.'}, status=500)

    try:
        max_results = min(int(max_results), 40)
    except ValueError:
        max_results = 20

    try:
        start_index = max(0, int(start_index))
    except ValueError:
        start_index = 0

    encoded_query = urllib.parse.quote(query)
    url = (
        f'https://www.googleapis.com/books/v1/volumes'
        f'?q={encoded_query}&maxResults={max_results}&startIndex={start_index}&key={api_key}'
    )

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            err_json = json.loads(body)
            msg = err_json.get('error', {}).get('message', str(e))
        except Exception:
            msg = str(e)
        return JsonResponse({'error': msg}, status=e.code)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    items = data.get('items', [])
    books = []
    favorite_ids = set(FavoriteBook.objects.values_list('google_books_id', flat=True))

    for item in items:
        info = item.get('volumeInfo', {})
        image_links = info.get('imageLinks', {})
        thumbnail = (
            image_links.get('thumbnail', '')
            or image_links.get('smallThumbnail', '')
        )
        # Upgrade to HTTPS
        if thumbnail.startswith('http://'):
            thumbnail = thumbnail.replace('http://', 'https://', 1)

        book_id = item.get('id', '')
        books.append({
            'google_books_id': book_id,
            'title': info.get('title', 'Unknown Title'),
            'authors': ', '.join(info.get('authors', [])),
            'description': info.get('description', ''),
            'thumbnail': thumbnail,
            'published_date': info.get('publishedDate', ''),
            'page_count': info.get('pageCount'),
            'categories': ', '.join(info.get('categories', [])),
            'average_rating': info.get('averageRating'),
            'is_favorite': book_id in favorite_ids,
        })

    return JsonResponse({
        'total_items': data.get('totalItems', 0),
        'start_index': start_index,
        'max_results': max_results,
        'books': books,
    })


@require_http_methods(["GET"])
def api_search_audiobooks(request):
    """
    GET /api/search-audiobooks/?q=<query>&page=<n>
    Search LibriVox for free public domain audiobooks.
    """
    query = request.GET.get('q', '').strip()
    page = request.GET.get('page', '1')

    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required.'}, status=400)

    try:
        page = max(1, int(page))
    except ValueError:
        page = 1

    limit = 12
    offset = (page - 1) * limit

    encoded_query = urllib.parse.quote(query)
    url = (
        f'https://librivox.org/api/feed/audiobooks'
        f'?title={encoded_query}&extended=1&format=json&limit={limit}&offset={offset}'
    )

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ReadPulse/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return JsonResponse({'audiobooks': [], 'total_results': 0, 'page': page})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    books_raw = data.get('books', []) or []
    audiobooks = []

    for ab in books_raw:
        # Build cover: LibriVox doesn't always have covers; use their default
        cover = ab.get('url_zip_file', '')  # placeholder, we'll use a generic approach

        # Authors from the readers/authors list
        authors_list = ab.get('authors', []) or []
        author_names = ', '.join(
            f"{a.get('first_name', '')} {a.get('last_name', '')}".strip()
            for a in authors_list
            if a.get('first_name') or a.get('last_name')
        ) or 'Unknown Author'

        audiobooks.append({
            'id': ab.get('id', ''),
            'title': ab.get('title', 'Unknown Title').strip(),
            'authors': author_names,
            'description': ab.get('description', '').strip(),
            'url_librivox': ab.get('url_librivox', ''),
            'url_rss': ab.get('url_rss', ''),
            'url_zip_file': ab.get('url_zip_file', ''),
            'language': ab.get('language', ''),
            'published': ab.get('copyright_year', ''),
            'num_sections': ab.get('num_sections', ''),
            'totaltime': ab.get('totaltime', ''),
        })

    # LibriVox API doesn't return total count cleanly; estimate from response size
    total_results = len(books_raw) + offset if len(books_raw) == limit else offset + len(books_raw)

    return JsonResponse({
        'audiobooks': audiobooks,
        'total_results': total_results,
        'page': page,
        'limit': limit,
    })


@require_http_methods(["GET"])
def api_list_favorites(request):
    """GET /api/favorites/ – return all saved favorites."""
    favorites = FavoriteBook.objects.all()
    return JsonResponse({'favorites': [f.to_dict() for f in favorites]})


@csrf_exempt
@require_http_methods(["POST"])
def api_add_favorite(request):
    """POST /api/favorites/add/ – save a book to favorites."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    google_books_id = payload.get('google_books_id', '').strip()
    if not google_books_id:
        return JsonResponse({'error': '"google_books_id" is required.'}, status=400)

    book, created = FavoriteBook.objects.get_or_create(
        google_books_id=google_books_id,
        defaults={
            'title': payload.get('title', ''),
            'authors': payload.get('authors', ''),
            'description': payload.get('description', ''),
            'thumbnail': payload.get('thumbnail', ''),
            'published_date': payload.get('published_date', ''),
            'page_count': payload.get('page_count'),
            'categories': payload.get('categories', ''),
            'average_rating': payload.get('average_rating'),
        },
    )

    status_code = 201 if created else 200
    return JsonResponse({
        'message': 'Added to favorites.' if created else 'Already in favorites.',
        'book': book.to_dict(),
    }, status=status_code)


@csrf_exempt
@require_http_methods(["DELETE"])
def api_remove_favorite(request, google_books_id):
    """DELETE /api/favorites/<google_books_id>/remove/ – remove a book from favorites."""
    book = get_object_or_404(FavoriteBook, google_books_id=google_books_id)
    book.delete()
    return JsonResponse({'message': 'Removed from favorites.'}, status=200)


@require_http_methods(["GET"])
def api_favorite_detail(request, google_books_id):
    """GET /api/favorites/<google_books_id>/ – check if a book is a favorite."""
    try:
        book = FavoriteBook.objects.get(google_books_id=google_books_id)
        return JsonResponse({'is_favorite': True, 'book': book.to_dict()})
    except FavoriteBook.DoesNotExist:
        return JsonResponse({'is_favorite': False})
