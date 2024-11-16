# Generated by Django 5.0.3 on 2024-11-10 09:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0006_lab_platform'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level_number', models.PositiveIntegerField(verbose_name='Вариант')),
                ('description', models.TextField(verbose_name='Описание варианта')),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='levels', to='interface.lab', verbose_name='Лабораторная работа')),
            ],
            options={
                'verbose_name': 'Уровень лаборатории',
                'verbose_name_plural': 'Уровни лабораторий',
                'ordering': ['lab', 'level_number'],
            },
        ),
        migrations.AddField(
            model_name='competition',
            name='level',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competitions', to='interface.lablevel', verbose_name='Вариант'),
        ),
        migrations.CreateModel(
            name='LabTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Описание задания')),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='interface.lab', verbose_name='Лабораторная работа')),
            ],
            options={
                'verbose_name': 'Задание',
                'verbose_name_plural': 'Задания',
            },
        ),
        migrations.AddField(
            model_name='competition',
            name='tasks',
            field=models.ManyToManyField(blank=True, to='interface.labtask', verbose_name='Задания'),
        ),
    ]