from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_favoritebook_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FavoriteAudiobook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('librivox_id', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=500)),
                ('authors', models.CharField(blank=True, default='', max_length=500)),
                ('description', models.TextField(blank=True, default='')),
                ('url_librivox', models.TextField(blank=True, default='')),
                ('url_rss', models.TextField(blank=True, default='')),
                ('url_zip_file', models.TextField(blank=True, default='')),
                ('language', models.CharField(blank=True, default='', max_length=100)),
                ('published', models.CharField(blank=True, default='', max_length=50)),
                ('num_sections', models.CharField(blank=True, default='', max_length=20)),
                ('totaltime', models.CharField(blank=True, default='', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='favorite_audiobooks',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='favoriteaudiobook',
            unique_together={('user', 'librivox_id')},
        ),
    ]
