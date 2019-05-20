from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator 
# Create your models here.

class CustomUser(AbstractUser):
    User_ID = models.IntegerField(primary_key=True,validators=[MinValueValidator(1)])
    AbstractUser._meta.get_field('email').blank=False

    def __str__(self):
        return self.username
