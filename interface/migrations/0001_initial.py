# Generated by Django 5.0.3 on 2024-04-07 09:07

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import django_summernote.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False, verbose_name='Имя')),
                ('description', models.TextField(verbose_name='Описание')),
                ('answer_flag', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Ответный флаг')),
                ('slug', models.SlugField(unique=True, verbose_name='Название в адресной строке')),
            ],
            options={
                'verbose_name': 'Лабораторная работа',
                'verbose_name_plural': 'Лабораторные работы',
            },
        ),
        migrations.CreateModel(
            name='MyAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, help_text='Defaults to filename, if left blank', max_length=255, null=True)),
                ('file', models.FileField(upload_to=django_summernote.utils.uploaded_filepath)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Прикрепленный файл',
                'verbose_name_plural': 'Прикрепленные файлы',
            },
        ),
        migrations.CreateModel(
            name='Platoon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='Номер взвода')),
            ],
            options={
                'verbose_name': 'Взвод',
                'verbose_name_plural': 'Взвода',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('platoon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='interface.platoon', verbose_name='взвод')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='IssuedLabs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_appointment', models.DateTimeField(verbose_name='Дата назначения')),
                ('end_date', models.DateTimeField(verbose_name='Дата окончания')),
                ('done', models.BooleanField(default=False, verbose_name='Завершено')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab_for_issue', to='interface.lab')),
            ],
            options={
                'verbose_name': 'Назначенная работа',
                'verbose_name_plural': 'Назначенные работы',
            },
        ),
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lab', to='interface.lab')),
            ],
            options={
                'verbose_name': 'Ответ',
                'verbose_name_plural': 'Ответы',
            },
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True, verbose_name='Название в адресной строке')),
                ('start', models.DateTimeField(verbose_name='Начало')),
                ('finish', models.DateTimeField(verbose_name='Конец')),
                ('participants', models.IntegerField(null=True)),
                ('lab', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competitions', to='interface.lab', verbose_name='Лабораторная работа')),
                ('platoons', models.ManyToManyField(to='interface.platoon')),
            ],
            options={
                'verbose_name': 'Соревнование',
                'verbose_name_plural': 'Соревнования',
            },
        ),
    ]
