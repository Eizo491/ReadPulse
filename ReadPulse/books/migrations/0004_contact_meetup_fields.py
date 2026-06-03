from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_bookrequest_swap_book'),
    ]

    operations = [
        # CommunityBook: owner contact info & preferred location
        migrations.AddField(
            model_name='communitybook',
            name='contact_info',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        migrations.AddField(
            model_name='communitybook',
            name='location',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
        # BookRequest: requester-proposed meetup datetime & location
        migrations.AddField(
            model_name='bookrequest',
            name='meetup_datetime',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='bookrequest',
            name='meetup_location',
            field=models.CharField(blank=True, default='', max_length=300),
        ),
    ]
