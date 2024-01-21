from django.db import models


class Lab(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    description = models.TextField()
    answer_flag = models.CharField(max_length=1024)
    

