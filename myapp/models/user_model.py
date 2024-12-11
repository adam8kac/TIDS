from django.db import models


class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.name
