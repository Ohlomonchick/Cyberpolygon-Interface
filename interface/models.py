from django.db import models
from django.utils.text import slugify
from django_summernote.models import AbstractAttachment
from django.contrib.auth.models import AbstractUser


class Lab(models.Model):
    name = models.CharField('Имя', max_length=255, primary_key=True)
    description = models.TextField('Описание')
    answer_flag = models.CharField('Ответный флаг', max_length=1024, null=True)
    slug = models.SlugField('Название в адресной строке', unique=True)

    class Meta:
        verbose_name = 'Лабораторная работа'
        verbose_name_plural = 'Лабораторные работы'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Lab, self).save(*args, **kwargs)


class MyAttachment(AbstractAttachment):
    class Meta:
        verbose_name = 'Прикрепленный файл'
        verbose_name_plural = 'Прикрепленные файлы'


class User(AbstractUser):
    name = models.CharField('Имя', max_length=127, null=True)
    second_name = models.CharField('Фамилия', max_length=127, null=True)
    platoon = models.CharField('Взвод', max_length=127, null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

