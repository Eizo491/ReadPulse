from django.db import models
from django.contrib.auth.models import User


class FavoriteBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', null=True, blank=True)
    google_books_id = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    thumbnail = models.TextField(blank=True, default='')
    published_date = models.CharField(max_length=50, blank=True, default='')
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(max_length=500, blank=True, default='')
    average_rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'google_books_id')

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'google_books_id': self.google_books_id,
            'title': self.title,
            'authors': self.authors,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'published_date': self.published_date,
            'page_count': self.page_count,
            'categories': self.categories,
            'average_rating': self.average_rating,
            'created_at': self.created_at.isoformat(),
            'is_favorite': True,
        }


class FavoriteAudiobook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_audiobooks', null=True, blank=True)
    librivox_id = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    url_librivox = models.TextField(blank=True, default='')
    url_rss = models.TextField(blank=True, default='')
    url_zip_file = models.TextField(blank=True, default='')
    language = models.CharField(max_length=100, blank=True, default='')
    published = models.CharField(max_length=50, blank=True, default='')
    num_sections = models.CharField(max_length=20, blank=True, default='')
    totaltime = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'librivox_id')

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'librivox_id': self.librivox_id,
            'title': self.title,
            'authors': self.authors,
            'description': self.description,
            'url_librivox': self.url_librivox,
            'url_rss': self.url_rss,
            'url_zip_file': self.url_zip_file,
            'language': self.language,
            'published': self.published,
            'num_sections': self.num_sections,
            'totaltime': self.totaltime,
            'created_at': self.created_at.isoformat(),
            'is_favorite': True,
        }


class CommunityBook(models.Model):
    LISTING_TYPE_CHOICES = [
        ('borrow', 'Available to Borrow'),
        ('swap', 'Available to Swap'),
        ('both', 'Borrow or Swap'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('swapped', 'Swapped'),
        ('unavailable', 'Unavailable'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_books')
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    thumbnail = models.TextField(blank=True, default='')
    published_date = models.CharField(max_length=50, blank=True, default='')
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(max_length=500, blank=True, default='')
    isbn = models.CharField(max_length=30, blank=True, default='')
    publisher = models.CharField(max_length=300, blank=True, default='')
    language = models.CharField(max_length=50, blank=True, default='')
    google_books_id = models.CharField(max_length=100, blank=True, default='')
    listing_type = models.CharField(max_length=10, choices=LISTING_TYPE_CHOICES, default='borrow')
    condition = models.CharField(max_length=100, blank=True, default='Good')
    notes = models.TextField(blank=True, default='')
    # Owner contact & meetup details
    contact_info = models.CharField(max_length=300, blank=True, default='')
    location = models.CharField(max_length=300, blank=True, default='')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.owner.username})"

    def to_dict(self, request_user=None):
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'owner_username': self.owner.username,
            'owner_name': self.owner.get_full_name() or self.owner.username,
            'title': self.title,
            'authors': self.authors,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'published_date': self.published_date,
            'page_count': self.page_count,
            'categories': self.categories,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'language': self.language,
            'google_books_id': self.google_books_id,
            'listing_type': self.listing_type,
            'condition': self.condition,
            'notes': self.notes,
            'contact_info': self.contact_info,
            'location': self.location,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'is_own': request_user and request_user.id == self.owner_id,
        }


class BookRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('borrow', 'Borrow'),
        ('swap', 'Swap'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    community_book = models.ForeignKey(CommunityBook, on_delete=models.CASCADE, related_name='requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_requests_made')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    # Meetup details — proposed by requester
    meetup_datetime = models.CharField(max_length=200, blank=True, default='')
    meetup_location = models.CharField(max_length=300, blank=True, default='')
    # Swap offer — filled only when request_type == 'swap'
    swap_book_title = models.CharField(max_length=500, blank=True, default='')
    swap_book_authors = models.CharField(max_length=500, blank=True, default='')
    swap_book_thumbnail = models.TextField(blank=True, default='')
    swap_book_condition = models.CharField(max_length=100, blank=True, default='Good')
    swap_book_description = models.TextField(blank=True, default='')
    swap_book_google_id = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('community_book', 'requester', 'request_type')

    def __str__(self):
        return f"{self.requester.username} → {self.community_book.title} ({self.request_type})"

    def to_dict(self, perspective='requester'):
        return {
            'id': self.id,
            'book_id': self.community_book_id,
            'book_title': self.community_book.title,
            'book_thumbnail': self.community_book.thumbnail,
            'book_authors': self.community_book.authors,
            'book_owner_username': self.community_book.owner.username,
            'book_owner_name': self.community_book.owner.get_full_name() or self.community_book.owner.username,
            'book_contact_info': self.community_book.contact_info,
            'book_location': self.community_book.location,
            'requester_id': self.requester_id,
            'requester_username': self.requester.username,
            'requester_name': self.requester.get_full_name() or self.requester.username,
            'request_type': self.request_type,
            'message': self.message,
            'status': self.status,
            # Meetup
            'meetup_datetime': self.meetup_datetime,
            'meetup_location': self.meetup_location,
            # Swap offer details
            'swap_book_title': self.swap_book_title,
            'swap_book_authors': self.swap_book_authors,
            'swap_book_thumbnail': self.swap_book_thumbnail,
            'swap_book_condition': self.swap_book_condition,
            'swap_book_description': self.swap_book_description,
            'swap_book_google_id': self.swap_book_google_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
