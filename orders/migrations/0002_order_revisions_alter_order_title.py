# Generated by Django 5.1.7 on 2025-03-23 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='revisions',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
