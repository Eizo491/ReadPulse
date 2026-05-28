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
            'page_count': self.page_count,
            'categories': self.categories,
            'average_rating': self.average_rating,
            'created_at': self.created_at.isoformat(),
        }
