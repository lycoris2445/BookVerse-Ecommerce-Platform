from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from ...models import Book, Author, Category, Publisher
from .serializers import BookSerializer, AuthorSerializer, CategorySerializer, PublisherSerializer


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [AllowAny]  # Allow public access to books
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['Title', 'Description']
    ordering_fields = ['Title', 'Price', 'PublicationDate']
    ordering = ['Title']


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [AllowAny]  # Allow public access to authors
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['AuthorName']
    ordering = ['AuthorName']


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]  # Allow public access to categories
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['CategoryName']
    ordering = ['CategoryName']


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['PublisherName']
    ordering = ['PublisherName']
