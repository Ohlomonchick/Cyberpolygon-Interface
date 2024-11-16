# Generated by Django 5.0.3 on 2024-11-10 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0007_lablevel_competition_level_labtask_competition_tasks'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lablevel',
            options={'ordering': ['lab', 'level_number'], 'verbose_name': 'Вариант', 'verbose_name_plural': 'Варианты'},
        ),
        migrations.AddField(
            model_name='labtask',
            name='task_id',
            field=models.CharField(max_length=255, null=True, verbose_name='Идентификатор задания'),
        ),
    ]