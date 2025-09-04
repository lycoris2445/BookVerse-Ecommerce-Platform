from django.db import models
from django.conf import settings


class Author(models.Model):
    AuthorID = models.AutoField(primary_key=True, db_column='AuthorID')
    AuthorName = models.CharField(max_length=255, db_column='AuthorName')
    Biography = models.TextField(null=True, blank=True, db_column='Biography')

    class Meta:
        managed = False
        db_table = 'author'

    def __str__(self):
        return self.AuthorName


class Publisher(models.Model):
    PublisherID = models.AutoField(primary_key=True, db_column='PublisherID')
    PublisherName = models.CharField(max_length=255, db_column='PublisherName')
    Address = models.TextField(null=True, blank=True, db_column='Address')
    ContactInfo = models.CharField(max_length=255, null=True, blank=True, db_column='ContactInfo')

    class Meta:
        managed = False
        db_table = 'publisher'

    def __str__(self):
        return self.PublisherName


class Category(models.Model):
    CategoryID = models.AutoField(primary_key=True, db_column='CategoryID')
    CategoryName = models.CharField(max_length=100, db_column='CategoryName')
    # Description field removed - doesn't exist in database schema

    class Meta:
        managed = False
        db_table = 'category'

    def __str__(self):
        return self.CategoryName


class Book(models.Model):
    BookID = models.AutoField(primary_key=True, db_column='BookID')
    Title = models.CharField(max_length=255, db_column='Title')
    AuthorID = models.IntegerField(null=True, blank=True, db_column='AuthorID')
    PublisherID = models.IntegerField(null=True, blank=True, db_column='PublisherID')
    CategoryID = models.IntegerField(null=True, blank=True, db_column='CategoryID')
    Price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='Price')
    Stock = models.IntegerField(null=True, blank=True, db_column='Stock')
    Description = models.TextField(null=True, blank=True, db_column='Description')
    PublicationDate = models.DateField(null=True, blank=True, db_column='PublicationDate')
    ImageURL = models.URLField(null=True, blank=True, db_column='ImageURL')

    class Meta:
        managed = False
        db_table = 'book'

    def __str__(self):
        return self.Title
