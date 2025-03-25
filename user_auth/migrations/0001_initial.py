# Generated by Django 5.1.7 on 2025-03-13 18:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(error_messages={'unique': 'Email bereits vorhanden.'}, max_length=254, unique=True)),
                ('username', models.CharField(default='Max Coderr', max_length=120)),
                ('type', models.CharField(choices=[('business', 'business'), ('customer', 'customer')], max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('first_name', models.CharField(default='Max', max_length=80)),
                ('last_name', models.CharField(default='Coderr', max_length=80)),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/')),
                ('location', models.CharField(blank=True, default='Berlin', max_length=100)),
                ('description', models.TextField(blank=True, max_length=1000)),
                ('working_hours', models.CharField(blank=True, default='9:00 - 17:00', max_length=100)),
                ('tel', models.CharField(blank=True, default='0123456789', max_length=25)),
                ('upload_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
