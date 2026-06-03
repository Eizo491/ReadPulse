from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_community_books'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_title',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_authors',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_thumbnail',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_condition',
            field=models.CharField(blank=True, default='Good', max_length=100),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='swap_book_google_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
