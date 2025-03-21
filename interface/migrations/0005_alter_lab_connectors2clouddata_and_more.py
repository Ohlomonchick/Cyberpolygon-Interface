# Generated by Django 5.0.3 on 2024-11-09 19:59

import interface.models
import interface.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0004_alter_competition_options_lab_connectors2clouddata_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lab',
            name='Connectors2CloudData',
            field=models.JSONField(default=interface.models.default_json, validators=[interface.validators.validate_top_level_array], verbose_name='Облачные коннекторы'),
        ),
        migrations.AlterField(
            model_name='lab',
            name='ConnectorsData',
            field=models.JSONField(default=interface.models.default_json, validators=[interface.validators.validate_top_level_array], verbose_name='Коннекторы'),
        ),
        migrations.AlterField(
            model_name='lab',
            name='NetworksData',
            field=models.JSONField(default=interface.models.default_json, validators=[interface.validators.validate_top_level_array], verbose_name='Сети'),
        ),
        migrations.AlterField(
            model_name='lab',
            name='NodesData',
            field=models.JSONField(default=interface.models.default_json, validators=[interface.validators.validate_top_level_array], verbose_name='Ноды'),
        ),
    ]
