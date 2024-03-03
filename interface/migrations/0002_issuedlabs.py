# Generated by Django 4.2.9 on 2024-02-29 13:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssuedLabs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_appointment', models.DateField(verbose_name='Дата назначения')),
                ('end_date', models.DateField(verbose_name='Дата окончания')),
                ('done', models.BooleanField(verbose_name='Завершено')),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab_for_issue', to='interface.lab')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Назначенная работа',
                'verbose_name_plural': 'Назначенные работы',
            },
        ),
    ]