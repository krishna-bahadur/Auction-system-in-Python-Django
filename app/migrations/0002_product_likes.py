# Generated by Django 4.0.3 on 2022-06-14 18:05

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='likes',
            field=models.ManyToManyField(related_name='Post_likes', to=settings.AUTH_USER_MODEL),
        ),
    ]
