import json
import urllib.request
import urllib.parse
import urllib.error

from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .models import FavoriteBook, CommunityBook, BookRequest


# ─────────────────────────────────────────────
# Page views
# ─────────────────────────────────────────────

@login_required
def search_page(request):
    fav_count = FavoriteBook.objects.filter(user=request.user).count()
    return render(request, 'books/search.html', {'fav_count': fav_count})


@login_required
def book_detail_page(request, google_books_id):
    fav_count = FavoriteBook.objects.filter(user=request.user).count()
    return render(request, 'books/book_detail.html', {
        'google_books_id': google_books_id,
        'fav_count': fav_count,
    })


@login_required
def favorites_page(request):
    favorites = FavoriteBook.objects.filter(user=request.user)
    return render(request, 'books/favorites.html', {
        'favorites': favorites,
        'fav_count': favorites.count(),
    })


@login_required
def community_page(request):
    fav_count = FavoriteBook.objects.filter(user=request.user).count()
    return render(request, 'books/community.html', {'fav_count': fav_count})


@login_required
def my_listings_page(request):
    fav_count = FavoriteBook.objects.filter(user=request.user).count()
    return render(request, 'books/my_listings.html', {'fav_count': fav_count})


@login_required
def requests_page(request):
    fav_count = FavoriteBook.objects.filter(user=request.user).count()
    return render(request, 'books/requests.html', {'fav_count': fav_count})


# ─────────────────────────────────────────────
# RESTful API  –  Google Books
# ─────────────────────────────────────────────

@require_http_methods(["GET"])
def api_book_detail(request, google_books_id):
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

    thumbnail = (
        image_links.get('extraLarge', '')
        or image_links.get('large', '')
        or image_links.get('medium', '')
        or image_links.get('small', '')
        or image_links.get('thumbnail', '')
        or image_links.get('smallThumbnail', '')
    )
    if thumbnail:
        import re
        thumbnail = re.sub(r'&?fife=\S+', '', thumbnail)
        thumbnail = re.sub(r'zoom=\d+', 'zoom=1', thumbnail)
        sep = '&' if '?' in thumbnail else '?'
        thumbnail = thumbnail.rstrip('&') + f'{sep}fife=w600'
    if thumbnail.startswith('http://'):
        thumbnail = thumbnail.replace('http://', 'https://', 1)

    favorite_ids = set(FavoriteBook.objects.filter(user=request.user).values_list('google_books_id', flat=True)) if request.user.is_authenticated else set()

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


@login_required
@require_http_methods(["GET"])
def api_search_books(request):
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
    favorite_ids = set(FavoriteBook.objects.filter(user=request.user).values_list('google_books_id', flat=True))

    for item in items:
        info = item.get('volumeInfo', {})
        image_links = info.get('imageLinks', {})
        thumbnail = (
            image_links.get('thumbnail', '')
            or image_links.get('smallThumbnail', '')
        )
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
    except urllib.error.HTTPError:
        return JsonResponse({'audiobooks': [], 'total_results': 0, 'page': page})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    books_raw = data.get('books', []) or []
    audiobooks = []

    for ab in books_raw:
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

    total_results = len(books_raw) + offset if len(books_raw) == limit else offset + len(books_raw)

    return JsonResponse({
        'audiobooks': audiobooks,
        'total_results': total_results,
        'page': page,
        'limit': limit,
    })


def api_audiobook_rss_proxy(request):
    """Proxy LibriVox RSS feed to avoid CORS issues in the browser."""
    rss_url = request.GET.get('url', '').strip()

    # Only allow LibriVox RSS URLs
    if not rss_url.startswith('https://librivox.org/rss/') and \
       not rss_url.startswith('http://librivox.org/rss/'):
        return JsonResponse({'error': 'Invalid RSS URL'}, status=400)

    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'ReadPulse/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read().decode('utf-8')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        return JsonResponse({'error': f'XML parse error: {e}'}, status=500)

    channel = root.find('channel')
    if channel is None:
        return JsonResponse({'chapters': []})

    chapters = []
    for item in channel.findall('item'):
        title_el = item.find('title')
        enclosure = item.find('enclosure')
        duration_el = item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
        if enclosure is not None:
            chapters.append({
                'title': title_el.text.strip() if title_el is not None and title_el.text else 'Chapter',
                'url': enclosure.get('url', ''),
                'type': enclosure.get('type', 'audio/mpeg'),
                'duration': duration_el.text.strip() if duration_el is not None and duration_el.text else '',
            })

    return JsonResponse({'chapters': chapters})


# ─────────────────────────────────────────────
# RESTful API  –  Favorites
# ─────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_list_favorites(request):
    favorites = FavoriteBook.objects.filter(user=request.user)
    return JsonResponse({'favorites': [f.to_dict() for f in favorites]})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_add_favorite(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    google_books_id = payload.get('google_books_id', '').strip()
    if not google_books_id:
        return JsonResponse({'error': '"google_books_id" is required.'}, status=400)

    book, created = FavoriteBook.objects.get_or_create(
        user=request.user,
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


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def api_remove_favorite(request, google_books_id):
    try:
        book = FavoriteBook.objects.get(user=request.user, google_books_id=google_books_id)
    except FavoriteBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found in favorites.'}, status=404)
    book.delete()
    return JsonResponse({'message': 'Removed from favorites.'}, status=200)


@login_required
@require_http_methods(["GET"])
def api_favorite_detail(request, google_books_id):
    try:
        book = FavoriteBook.objects.get(user=request.user, google_books_id=google_books_id)
        return JsonResponse({'is_favorite': True, 'book': book.to_dict()})
    except FavoriteBook.DoesNotExist:
        return JsonResponse({'is_favorite': False})


# ─────────────────────────────────────────────
# RESTful API  –  Community Books
# ─────────────────────────────────────────────

@login_required
@require_http_methods(["GET"])
def api_community_books(request):
    """GET /api/community/ – list all available community books (excluding own)."""
    listing_type = request.GET.get('type', '')
    search = request.GET.get('q', '').strip()

    qs = CommunityBook.objects.filter(status='available').select_related('owner')
    if listing_type in ('borrow', 'swap'):
        qs = qs.filter(Q(listing_type=listing_type) | Q(listing_type='both'))
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(authors__icontains=search) | Q(categories__icontains=search))

    books = [b.to_dict(request_user=request.user) for b in qs]
    return JsonResponse({'books': books, 'total': len(books)})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_add_community_book(request):
    """POST /api/community/add/ – list a book in community."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    title = payload.get('title', '').strip()
    if not title:
        return JsonResponse({'error': '"title" is required.'}, status=400)

    listing_type = payload.get('listing_type', 'borrow')
    if listing_type not in ('borrow', 'swap', 'both'):
        listing_type = 'borrow'

    book = CommunityBook.objects.create(
        owner=request.user,
        title=title,
        authors=payload.get('authors', ''),
        description=payload.get('description', ''),
        thumbnail=payload.get('thumbnail', ''),
        published_date=payload.get('published_date', ''),
        page_count=payload.get('page_count'),
        categories=payload.get('categories', ''),
        isbn=payload.get('isbn', ''),
        publisher=payload.get('publisher', ''),
        language=payload.get('language', ''),
        google_books_id=payload.get('google_books_id', ''),
        listing_type=listing_type,
        condition=payload.get('condition', 'Good'),
        notes=payload.get('notes', ''),
        contact_info=payload.get('contact_info', ''),
        location=payload.get('location', ''),
    )
    return JsonResponse({'message': 'Book listed successfully.', 'book': book.to_dict(request_user=request.user)}, status=201)


@login_required
@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def api_community_book_detail(request, book_id):
    """PATCH or DELETE /api/community/<id>/ – update or remove own listing."""
    book = get_object_or_404(CommunityBook, id=book_id, owner=request.user)

    if request.method == 'DELETE':
        book.delete()
        return JsonResponse({'message': 'Listing removed.'})

    # PATCH
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    for field in ('title', 'authors', 'isbn', 'published_date', 'description',
                  'categories', 'publisher', 'language', 'google_books_id',
                  'listing_type', 'condition', 'notes', 'status',
                  'contact_info', 'location'):
        if field in payload:
            setattr(book, field, payload[field])
    # thumbnail — allow update
    if 'thumbnail' in payload:
        book.thumbnail = payload['thumbnail']
    if 'page_count' in payload:
        book.page_count = payload['page_count'] or None
        if field in payload:
            setattr(book, field, payload[field])
    book.save()
    return JsonResponse({'message': 'Listing updated.', 'book': book.to_dict(request_user=request.user)})


@login_required
@require_http_methods(["GET"])
def api_my_listings(request):
    """GET /api/community/my-listings/ – current user's listed books."""
    books = CommunityBook.objects.filter(owner=request.user).select_related('owner')
    return JsonResponse({'books': [b.to_dict(request_user=request.user) for b in books]})


@login_required
@require_http_methods(["GET"])
def api_my_available_listings(request):
    """GET /api/community/my-available-listings/ – own books available (for swap picker)."""
    books = CommunityBook.objects.filter(owner=request.user, status='available').select_related('owner')
    return JsonResponse({'books': [b.to_dict(request_user=request.user) for b in books]})


# ─────────────────────────────────────────────
# RESTful API  –  Book Requests
# ─────────────────────────────────────────────

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def api_create_request(request):
    """POST /api/requests/create/ – send a borrow/swap request."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    book_id = payload.get('book_id')
    request_type = payload.get('request_type', 'borrow')

    if not book_id:
        return JsonResponse({'error': '"book_id" is required.'}, status=400)
    if request_type not in ('borrow', 'swap'):
        return JsonResponse({'error': 'Invalid request_type.'}, status=400)

    community_book = get_object_or_404(CommunityBook, id=book_id, status='available')

    if community_book.owner == request.user:
        return JsonResponse({'error': 'You cannot request your own book.'}, status=400)

    # Check listing type allows this request type
    if community_book.listing_type not in (request_type, 'both'):
        return JsonResponse({'error': f'This book is not available for {request_type}.'}, status=400)

    book_request, created = BookRequest.objects.get_or_create(
        community_book=community_book,
        requester=request.user,
        request_type=request_type,
        defaults={
            'message': payload.get('message', ''),
            'status': 'pending',
            'meetup_datetime': payload.get('meetup_datetime', ''),
            'meetup_location': payload.get('meetup_location', ''),
            'swap_book_title': payload.get('swap_book_title', '') if request_type == 'swap' else '',
            'swap_book_authors': payload.get('swap_book_authors', '') if request_type == 'swap' else '',
            'swap_book_thumbnail': payload.get('swap_book_thumbnail', '') if request_type == 'swap' else '',
            'swap_book_condition': payload.get('swap_book_condition', 'Good') if request_type == 'swap' else '',
            'swap_book_description': payload.get('swap_book_description', '') if request_type == 'swap' else '',
            'swap_book_google_id': payload.get('swap_book_google_id', '') if request_type == 'swap' else '',
        },
    )

    if not created:
        if book_request.status in ('cancelled', 'declined'):
            book_request.status = 'pending'
            book_request.message = payload.get('message', book_request.message)
            book_request.meetup_datetime = payload.get('meetup_datetime', book_request.meetup_datetime)
            book_request.meetup_location = payload.get('meetup_location', book_request.meetup_location)
            if request_type == 'swap':
                book_request.swap_book_title = payload.get('swap_book_title', book_request.swap_book_title)
                book_request.swap_book_authors = payload.get('swap_book_authors', book_request.swap_book_authors)
                book_request.swap_book_thumbnail = payload.get('swap_book_thumbnail', book_request.swap_book_thumbnail)
                book_request.swap_book_condition = payload.get('swap_book_condition', book_request.swap_book_condition)
                book_request.swap_book_description = payload.get('swap_book_description', book_request.swap_book_description)
                book_request.swap_book_google_id = payload.get('swap_book_google_id', book_request.swap_book_google_id)
            book_request.save()
            return JsonResponse({'message': 'Request re-sent.', 'request': book_request.to_dict()}, status=200)
        return JsonResponse({'message': 'Request already exists.', 'request': book_request.to_dict()}, status=200)

    return JsonResponse({'message': 'Request sent successfully.', 'request': book_request.to_dict()}, status=201)


@login_required
@require_http_methods(["GET"])
def api_my_requests(request):
    """GET /api/requests/mine/ – requests made by current user."""
    requests_qs = BookRequest.objects.filter(requester=request.user).select_related('community_book', 'community_book__owner', 'requester')
    return JsonResponse({'requests': [r.to_dict('requester') for r in requests_qs]})


@login_required
@require_http_methods(["GET"])
def api_requests_for_me(request):
    """GET /api/requests/for-me/ – requests on current user's listings."""
    requests_qs = BookRequest.objects.filter(community_book__owner=request.user).select_related('community_book', 'community_book__owner', 'requester')
    return JsonResponse({'requests': [r.to_dict('owner') for r in requests_qs]})


@login_required
@csrf_exempt
@require_http_methods(["PATCH"])
def api_update_request(request, request_id):
    """PATCH /api/requests/<id>/ – update status of a request."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    new_status = payload.get('status', '')

    # Determine who is acting
    try:
        book_request = BookRequest.objects.select_related('community_book', 'community_book__owner', 'requester').get(id=request_id)
    except BookRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)

    is_owner = book_request.community_book.owner == request.user
    is_requester = book_request.requester == request.user

    if not is_owner and not is_requester:
        return JsonResponse({'error': 'Permission denied.'}, status=403)

    # Owner can accept, decline, complete
    if is_owner and new_status in ('accepted', 'declined', 'completed'):
        book_request.status = new_status
        if new_status == 'accepted':
            # Mark book as borrowed/swapped
            book_request.community_book.status = 'borrowed' if book_request.request_type == 'borrow' else 'swapped'
            book_request.community_book.save()
        book_request.save()
        return JsonResponse({'message': f'Request {new_status}.', 'request': book_request.to_dict()})

    # Requester can cancel
    if is_requester and new_status == 'cancelled':
        book_request.status = 'cancelled'
        book_request.save()
        return JsonResponse({'message': 'Request cancelled.', 'request': book_request.to_dict()})

    # Requester can return a borrowed book (accepted borrow → completed + book back to available)
    if is_requester and new_status == 'returned':
        if book_request.request_type != 'borrow' or book_request.status != 'accepted':
            return JsonResponse({'error': 'Only accepted borrow requests can be returned.'}, status=400)
        book_request.status = 'completed'
        book_request.community_book.status = 'available'
        book_request.community_book.save()
        book_request.save()
        return JsonResponse({'message': 'Book returned successfully.', 'request': book_request.to_dict()})

    return JsonResponse({'error': 'Invalid status transition.'}, status=400)
