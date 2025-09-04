from rest_framework import serializers
from ...models import Book, Author, Category, Publisher


def get_absolute_image_url(image_path, request=None):
    """Convert relative image path to absolute URL - same as recommendation service"""
    if not image_path:
        return ''
    if image_path.startswith(('http://', 'https://')):
        return image_path
    
    # Try to get base URL from Django settings or request
    from django.conf import settings
    
    # Use BACKEND_URL from environment if set, otherwise construct from request
    base_url = getattr(settings, 'BACKEND_URL', None)
    if not base_url:
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            # Fallback for local development
            base_url = "http://127.0.0.1:8000"
    
    if image_path.startswith('/'):
        return f"{base_url}{image_path}"
    return f"{base_url}/media/{image_path}"


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['AuthorID', 'AuthorName', 'Biography']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['PublisherID', 'PublisherName', 'Address', 'ContactInfo']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['CategoryID', 'CategoryName']  # Removed Description field


class BookSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = ['BookID', 'Title', 'AuthorID', 'PublisherID', 'CategoryID', 
                  'Price', 'Stock', 'Description', 'PublicationDate', 'image_url']
    
    def get_image_url(self, obj):
        """Use the same image URL logic as recommendation service"""
        request = self.context.get('request')
        return get_absolute_image_url(obj.ImageURL, request)
