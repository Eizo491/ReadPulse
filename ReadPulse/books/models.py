from django.db import models


class FavoriteBook(models.Model):
    google_books_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    thumbnail = models.URLField(max_length=1000, blank=True, default='')
    published_date = models.CharField(max_length=50, blank=True, default='')
    page_count = models.IntegerField(null=True, blank=True)
    categories = models.CharField(max_length=500, blank=True, default='')
    average_rating = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CommunityBook(models.Model):

    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('worn', 'Worn'),
    ]

    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')
    thumbnail = models.TextField(blank=True, default='')
    published_date = models.CharField(max_length=50, blank=True, default='')
    categories = models.CharField(max_length=500, blank=True, default='')
    google_books_id = models.CharField(max_length=100, blank=True, default='')

    owner_name = models.CharField(max_length=200)
    owner_contact = models.CharField(max_length=300, blank=True, default='')
    location = models.CharField(max_length=300, blank=True, default='')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    notes = models.TextField(blank=True, default='')

    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'id': self.id,
            'google_books_id': self.google_books_id,
            'title': self.title,
            'authors': self.authors,
            'description': self.description,
            'thumbnail': self.thumbnail,
            'published_date': self.published_date,
            'categories': self.categories,
            'owner_name': self.owner_name,
            'owner_contact': self.owner_contact,
            'location': self.location,
            'condition': self.condition,
            'condition_display': self.get_condition_display(),
            'notes': self.notes,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat(),
        }


class BorrowRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('returned', 'Returned'),
    ]

    book = models.ForeignKey(CommunityBook, on_delete=models.CASCADE, related_name='borrow_requests')
    requester_name = models.CharField(max_length=200)
    requester_contact = models.CharField(max_length=300)
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester_name} → {self.book.title} [{self.status}]"

    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'book_title': self.book.title,
            'book_owner': self.book.owner_name,
            'requester_name': self.requester_name,
            'requester_contact': self.requester_contact,
            'message': self.message,
            'status': self.status,
            'status_display': self.get_status_display(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }