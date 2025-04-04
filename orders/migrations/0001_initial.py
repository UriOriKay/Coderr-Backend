# Generated by Django 5.1.7 on 2025-03-16 09:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('offers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_user', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('cancelled', 'Cancelled'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='in_progress', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.IntegerField(blank=True, null=True)),
                ('delivery_time_in_days', models.IntegerField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('features', models.JSONField(blank=True, null=True)),
                ('offer_type', models.CharField(blank=True, max_length=50)),
                ('business_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Business User')),
                ('offer_detail_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='offers.offerdetail', verbose_name='Offer Detail')),
            ],
        ),
    ]
