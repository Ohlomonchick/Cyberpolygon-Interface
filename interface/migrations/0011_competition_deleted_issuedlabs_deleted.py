# Generated by Django 5.0.3 on 2024-11-17 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0010_alter_issuedlabs_date_of_appointment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='competition',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='issuedlabs',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]