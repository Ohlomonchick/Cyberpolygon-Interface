from django.db import models
from django.utils.text import slugify


class Lab(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    description = models.TextField()
    answer_flag = models.CharField(max_length=1024, null=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Lab, self).save(*args, **kwargs)

