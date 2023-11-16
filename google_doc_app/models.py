from django.db import models

class UploadedFile(models.Model):
    name = models.CharField(max_length=255)
    data = models.TextField()