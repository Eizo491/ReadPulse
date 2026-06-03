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

from .models import FavoriteBook, CommunityBook, BorrowRequest


# ─────────────────────────────────────────────
# Page views
# ─────────────────────────────────────────────

@login_required
def search_page(request):
    """Render the Search Books page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/search.html', {'fav_count': fav_count})


@login_required
def book_detail_page(request, google_books_id):
    """Render the Book Detail page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/book_detail.html', {
        'google_books_id': google_books_id,
        'fav_count': fav_count,
    })


@login_required
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
        cover = ab.get('url_zip_file', '')

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
    try:
        book = FavoriteBook.objects.get(google_books_id=google_books_id)
    except FavoriteBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found in favorites.'}, status=404)
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


# ─────────────────────────────────────────────
# Community Books – Page views
# ─────────────────────────────────────────────



@login_required
def community_page(request):
    """Render the Community Books listing page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/community.html', {'fav_count': fav_count})


@login_required
def community_book_detail_page(request, book_id):
    """Render a single community book's detail page."""
    book = get_object_or_404(CommunityBook, id=book_id)
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/community_detail.html', {
        'book': book,
        'fav_count': fav_count,
    })


# ─────────────────────────────────────────────
# Community Books – API
# ─────────────────────────────────────────────

@require_http_methods(["GET"])
def api_list_community_books(request):
    """GET /api/community/ – list all community books."""
    q = request.GET.get('q', '').strip()
    qs = CommunityBook.objects.all()
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(title__icontains=q) | Q(authors__icontains=q) | Q(location__icontains=q))
    books = [b.to_dict() for b in qs]
    return JsonResponse({'books': books, 'total': len(books)})


@csrf_exempt
@require_http_methods(["POST"])
def api_add_community_book(request):
    """POST /api/community/add/ – list a new community book."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    required = ['title', 'owner_name']
    for field in required:
        if not payload.get(field, '').strip():
            return JsonResponse({'error': f'"{field}" is required.'}, status=400)

    book = CommunityBook.objects.create(
        title=payload['title'].strip(),
        authors=payload.get('authors', '').strip(),
        description=payload.get('description', '').strip(),
        thumbnail=payload.get('thumbnail', '').strip(),
        published_date=payload.get('published_date', '').strip(),
        categories=payload.get('categories', '').strip(),
        google_books_id=payload.get('google_books_id', '').strip(),
        owner_name=payload['owner_name'].strip(),
        owner_contact=payload.get('owner_contact', '').strip(),
        location=payload.get('location', '').strip(),
        condition=payload.get('condition', 'good'),
        notes=payload.get('notes', '').strip(),
        listing_type=payload.get('listing_type', 'borrow'),
    )
    return JsonResponse({'message': 'Book listed successfully!', 'book': book.to_dict()}, status=201)


@require_http_methods(["GET"])
def api_community_book_detail(request, book_id):
    """GET /api/community/<id>/ – fetch a single community book with its requests."""
    try:
        book = CommunityBook.objects.get(id=book_id)
    except CommunityBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found.'}, status=404)
    data = book.to_dict()
    data['borrow_requests'] = [r.to_dict() for r in book.borrow_requests.all()]
    return JsonResponse({'book': data})


@csrf_exempt
@require_http_methods(["POST"])
def api_request_borrow(request, book_id):
    """POST /api/community/<id>/borrow/ – submit a borrow/swap request."""
    try:
        book = CommunityBook.objects.get(id=book_id)
    except CommunityBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found.'}, status=404)

    if not book.is_available:
        return JsonResponse({'error': 'This book is not available for borrowing right now.'}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    required = ['requester_name', 'requester_contact']
    for field in required:
        if not payload.get(field, '').strip():
            return JsonResponse({'error': f'"{field}" is required.'}, status=400)

    # Validate that request_type matches what the listing allows
    request_type = payload.get('request_type', 'borrow')
    valid_types = [t[0] for t in BorrowRequest.REQUEST_TYPE_CHOICES]
    if request_type not in valid_types:
        return JsonResponse({'error': f'Invalid request_type. Choose from: {", ".join(valid_types)}'}, status=400)

    if book.listing_type != 'both' and request_type != book.listing_type:
        return JsonResponse(
            {'error': f'This book is only available for "{book.listing_type}". Cannot request "{request_type}".'},
            status=400
        )

    # Parse meetup_datetime safely — HTML datetime-local sends "YYYY-MM-DDTHH:MM"
    # (no seconds), which Django's DateTimeField rejects. Normalise it here.
    meetup_datetime = None
    raw_dt = payload.get('meetup_datetime') or ''
    if raw_dt.strip():
        from django.utils.dateparse import parse_datetime
        # Append seconds if missing (e.g. "2026-03-06T05:16" → "2026-03-06T05:16:00")
        if raw_dt.count(':') == 1:
            raw_dt = raw_dt + ':00'
        meetup_datetime = parse_datetime(raw_dt)
        if meetup_datetime is None:
            return JsonResponse({'error': 'Invalid meetup_datetime format. Use YYYY-MM-DDTHH:MM.'}, status=400)

    borrow = BorrowRequest.objects.create(
        book=book,
        requester_name=payload['requester_name'].strip(),
        requester_contact=payload['requester_contact'].strip(),
        message=payload.get('message', '').strip(),
        meetup_datetime=meetup_datetime,
        request_type=request_type,
    )
    return JsonResponse({'message': 'Request submitted!', 'request': borrow.to_dict()}, status=201)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_update_borrow_status(request, request_id):
    """PATCH /api/community/requests/<id>/status/ – update borrow request status."""
    try:
        borrow = BorrowRequest.objects.get(id=request_id)
    except BorrowRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    new_status = payload.get('status', '').strip()
    valid = [s[0] for s in BorrowRequest.STATUS_CHOICES]
    if new_status not in valid:
        return JsonResponse({'error': f'Invalid status. Choose from: {", ".join(valid)}'}, status=400)

    borrow.status = new_status
    borrow.save()

    # Mark book unavailable when approved, available again when returned/declined
    if new_status == 'approved':
        borrow.book.is_available = False
        borrow.book.save()
    elif new_status in ('returned', 'declined'):
        borrow.book.is_available = True
        borrow.book.save()

    return JsonResponse({'message': 'Status updated.', 'request': borrow.to_dict()})


@login_required
def my_books_page(request):
    """Render the My Books page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/my_books.html', {'fav_count': fav_count})


@login_required
def my_requests_page(request):
    """Render the My Requests page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/my_requests.html', {'fav_count': fav_count})


@login_required
def requests_page(request):
    """Render the All Requests page."""
    fav_count = FavoriteBook.objects.count()
    return render(request, 'books/requests.html', {'fav_count': fav_count})


@csrf_exempt
@require_http_methods(["PATCH"])
def api_update_community_book(request, book_id):
    """PATCH /api/community/<id>/update/ – update a community book's details."""
    try:
        book = CommunityBook.objects.get(id=book_id)
    except CommunityBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found.'}, status=404)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    # listing_type added so owner can change borrow/return/both
    updatable = ['title', 'authors', 'description', 'condition', 'notes',
                 'location', 'owner_contact', 'is_available', 'listing_type']
    for field in updatable:
        if field in payload:
            val = payload[field]
            if isinstance(val, str):
                val = val.strip()
            # Validate listing_type
            if field == 'listing_type':
                valid_listing = [t[0] for t in CommunityBook.LISTING_TYPE_CHOICES]
                if val not in valid_listing:
                    return JsonResponse({'error': f'Invalid listing_type. Choose from: {", ".join(valid_listing)}'}, status=400)
            setattr(book, field, val)

    if not book.title:
        return JsonResponse({'error': '"title" cannot be empty.'}, status=400)

    book.save()
    return JsonResponse({'message': 'Book updated successfully!', 'book': book.to_dict()})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_community_book(request, book_id):
    """DELETE /api/community/<id>/delete/ – remove a community book listing."""
    try:
        book = CommunityBook.objects.get(id=book_id)
    except CommunityBook.DoesNotExist:
        return JsonResponse({'error': 'Book not found.'}, status=404)
    book.delete()
    return JsonResponse({'message': 'Book listing deleted.'}, status=200)


@csrf_exempt
@require_http_methods(["PATCH"])
def api_edit_borrow_request(request, request_id):
    """PATCH /api/community/requests/<id>/edit/ – requester edits their own borrow request (only if still pending)."""
    try:
        borrow = BorrowRequest.objects.get(id=request_id)
    except BorrowRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)

    if borrow.status != 'pending':
        return JsonResponse({'error': 'Only pending requests can be edited.'}, status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    editable = ['requester_name', 'requester_contact', 'message', 'request_type']
    for field in editable:
        if field in payload:
            val = payload[field]
            if isinstance(val, str):
                val = val.strip()
            setattr(borrow, field, val)

    # Handle meetup_datetime separately — datetime-local sends "YYYY-MM-DDTHH:MM" (no seconds)
    if 'meetup_datetime' in payload:
        raw_dt = payload['meetup_datetime'] or ''
        if not raw_dt.strip():
            borrow.meetup_datetime = None
        else:
            from django.utils.dateparse import parse_datetime
            if raw_dt.count(':') == 1:
                raw_dt = raw_dt + ':00'
            parsed = parse_datetime(raw_dt)
            if parsed is None:
                return JsonResponse({'error': 'Invalid meetup_datetime format. Use YYYY-MM-DDTHH:MM.'}, status=400)
            borrow.meetup_datetime = parsed

    borrow.save()
    return JsonResponse({'message': 'Request updated.', 'request': borrow.to_dict()})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_cancel_borrow_request(request, request_id):
    """DELETE /api/community/requests/<id>/cancel/ – requester cancels their own borrow request (only if still pending)."""
    try:
        borrow = BorrowRequest.objects.get(id=request_id)
    except BorrowRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)

    if borrow.status != 'pending':
        return JsonResponse({'error': 'Only pending requests can be cancelled.'}, status=400)

    borrow.delete()
    return JsonResponse({'message': 'Request cancelled.'}, status=200)


@require_http_methods(["GET"])
def api_get_borrow_request(request, request_id):
    """GET /api/community/requests/<id>/ – fetch a single borrow request by ID."""
    try:
        borrow = BorrowRequest.objects.get(id=request_id)
    except BorrowRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)
    return JsonResponse({'request': borrow.to_dict()})


@require_http_methods(["GET"])
def api_list_all_requests(request):
    """GET /api/community/all-requests/ – list all borrow/swap requests with optional filters."""
    status_filter = request.GET.get('status', '').strip()
    type_filter   = request.GET.get('type', '').strip()

    qs = BorrowRequest.objects.select_related('book').all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    if type_filter:
        qs = qs.filter(request_type=type_filter)

    return JsonResponse({'requests': [r.to_dict() for r in qs], 'total': qs.count()})


# ─────────────────────────────────────────────
# Session-backed My Books & My Requests APIs
# ─────────────────────────────────────────────

@require_http_methods(["GET"])
def api_session_my_books(request):
    """GET /api/session/my-books/ – return IDs for the current user.
    If logged in, queries the DB so listed books survive logout/login."""
    if request.user.is_authenticated:
        ids = list(CommunityBook.objects.filter(
            owner_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_books', [])
    return JsonResponse({'ids': ids})


@csrf_exempt
@require_http_methods(["POST"])
def api_session_add_my_book(request):
    """POST /api/session/my-books/ – record that this user owns a book."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    book_id = payload.get('id')
    if book_id is None:
        return JsonResponse({'error': '"id" is required.'}, status=400)

    if request.user.is_authenticated:
        CommunityBook.objects.filter(id=book_id).update(owner_user=request.user)
        ids = list(CommunityBook.objects.filter(
            owner_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_books', [])
        if book_id not in ids:
            ids.append(book_id)
            request.session['readpulse_my_books'] = ids
            request.session.modified = True
    return JsonResponse({'ids': ids})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_session_remove_my_book(request, book_id):
    """DELETE /api/session/my-books/<id>/ – disown a book."""
    if request.user.is_authenticated:
        CommunityBook.objects.filter(
            id=book_id, owner_user=request.user
        ).update(owner_user=None)
        ids = list(CommunityBook.objects.filter(
            owner_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_books', [])
        ids = [i for i in ids if i != book_id]
        request.session['readpulse_my_books'] = ids
        request.session.modified = True
    return JsonResponse({'ids': ids})


@require_http_methods(["GET"])
def api_session_my_requests(request):
    """GET /api/session/my-requests/ – return request IDs for the current user.
    If logged in, queries the DB so requests survive logout/login.
    Falls back to session for anonymous users."""
    if request.user.is_authenticated:
        ids = list(BorrowRequest.objects.filter(
            requester_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_requests', [])
    return JsonResponse({'ids': ids})


@csrf_exempt
@require_http_methods(["POST"])
def api_session_add_my_request(request):
    """POST /api/session/my-requests/ – record that this user owns a request."""
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)
    req_id = payload.get('id')
    if req_id is None:
        return JsonResponse({'error': '"id" is required.'}, status=400)

    if request.user.is_authenticated:
        # Link the request to the user in the DB
        BorrowRequest.objects.filter(id=req_id).update(requester_user=request.user)
        ids = list(BorrowRequest.objects.filter(
            requester_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_requests', [])
        if req_id not in ids:
            ids.append(req_id)
            request.session['readpulse_my_requests'] = ids
            request.session.modified = True
    return JsonResponse({'ids': ids})


@csrf_exempt
@require_http_methods(["DELETE"])
def api_session_remove_my_request(request, request_id):
    """DELETE /api/session/my-requests/<id>/ – disown a request."""
    if request.user.is_authenticated:
        BorrowRequest.objects.filter(
            id=request_id, requester_user=request.user
        ).update(requester_user=None)
        ids = list(BorrowRequest.objects.filter(
            requester_user=request.user
        ).values_list('id', flat=True))
    else:
        ids = request.session.get('readpulse_my_requests', [])
        ids = [i for i in ids if i != request_id]
        request.session['readpulse_my_requests'] = ids
        request.session.modified = True
    return JsonResponse({'ids': ids})