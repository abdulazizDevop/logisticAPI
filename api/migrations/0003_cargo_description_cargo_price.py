# Generated by Django 5.1.6 on 2025-03-10 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_user_groups_user_user_permissions'),
    ]

    operations = [
        migrations.AddField(
            model_name='cargo',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cargo',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
