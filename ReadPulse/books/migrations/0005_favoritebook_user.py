from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_contact_meetup_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Drop the old unique constraint on google_books_id
        migrations.AlterField(
            model_name='favoritebook',
            name='google_books_id',
            field=models.CharField(max_length=100),
        ),
        # 2. Add user FK (nullable so existing rows survive)
        migrations.AddField(
            model_name='favoritebook',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # 3. Add unique_together for (user, google_books_id)
        migrations.AlterUniqueTogether(
            name='favoritebook',
            unique_together={('user', 'google_books_id')},
        ),
    ]
