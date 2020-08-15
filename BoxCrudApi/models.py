from django.db import models
from django.contrib.auth.models import User

# Create your models here.



class Box(models.Model):
    length = models.FloatField()
    breadth = models.FloatField()
    height = models.FloatField()
    area = models.FloatField()
    volume = models.FloatField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_of_creation = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.created_by.username
