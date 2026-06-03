from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='FavoriteBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('google_books_id', models.CharField(max_length=100, unique=True)),
                ('title', models.CharField(max_length=500)),
                ('authors', models.CharField(blank=True, default='', max_length=500)),
                ('description', models.TextField(blank=True, default='')),
                ('thumbnail', models.TextField(blank=True, default='')),
                ('published_date', models.CharField(blank=True, default='', max_length=50)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('categories', models.CharField(blank=True, default='', max_length=500)),
                ('average_rating', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
