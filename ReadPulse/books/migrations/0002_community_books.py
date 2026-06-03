from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('authors', models.CharField(blank=True, default='', max_length=500)),
                ('description', models.TextField(blank=True, default='')),
                ('thumbnail', models.TextField(blank=True, default='')),
                ('published_date', models.CharField(blank=True, default='', max_length=50)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('categories', models.CharField(blank=True, default='', max_length=500)),
                ('isbn', models.CharField(blank=True, default='', max_length=30)),
                ('publisher', models.CharField(blank=True, default='', max_length=300)),
                ('language', models.CharField(blank=True, default='', max_length=50)),
                ('google_books_id', models.CharField(blank=True, default='', max_length=100)),
                ('listing_type', models.CharField(choices=[('borrow', 'Available to Borrow'), ('swap', 'Available to Swap'), ('both', 'Borrow or Swap')], default='borrow', max_length=10)),
                ('condition', models.CharField(blank=True, default='Good', max_length=100)),
                ('notes', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('available', 'Available'), ('borrowed', 'Borrowed'), ('swapped', 'Swapped'), ('unavailable', 'Unavailable')], default='available', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='community_books', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='BookRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_type', models.CharField(choices=[('borrow', 'Borrow'), ('swap', 'Swap')], max_length=10)),
                ('message', models.TextField(blank=True, default='')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('community_book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='books.communitybook')),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_requests_made', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterUniqueTogether(
            name='bookrequest',
            unique_together={('community_book', 'requester', 'request_type')},
        ),
    ]
