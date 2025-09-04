from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Customer(models.Model):
    CustomerID = models.AutoField(primary_key=True, db_column='CustomerID')
    FullName = models.CharField(max_length=255, db_column='FullName')
    Email = models.EmailField(unique=True, db_column='Email')
    Phone = models.CharField(max_length=20, null=True, blank=True, db_column='Phone')
    Address = models.TextField(null=True, blank=True, db_column='Address')
    PasswordHash = models.CharField(max_length=255, db_column='PasswordHash')
    CreatedAt = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')

    class Meta:
        managed = False
        db_table = 'customer'

    def __str__(self):
        return self.FullName
