# Generated by Django 5.0.3 on 2024-11-17 16:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0011_competition_deleted_issuedlabs_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuedlabs',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Кому назначаем'),
        ),
    ]
