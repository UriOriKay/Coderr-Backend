# Generated by Django 5.1.7 on 2025-03-16 12:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_auth', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='upload_at',
            new_name='uploaded_at',
        ),
    ]
