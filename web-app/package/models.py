from django.db import models
from users.models import CustomUser
# Create your models here.

class Package(models.Model):
    package_id = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    curr_x = models.IntegerField(blank=True, null=True)
    curr_y = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=200, default = 'created')
    items = models.CharField(max_length=200, default = '')
    amount = models.IntegerField()
    truck_id = models.IntegerField()
    owner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True)

class SearchPackage(models.Model):
    package_id = models.IntegerField()

class Comment(models.Model):
    owner = models.CharField(max_length=200)
    context = models.CharField(max_length=10000)
