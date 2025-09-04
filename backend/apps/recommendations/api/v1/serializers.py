from rest_framework import serializers
from apps.catalog.models import Book


class RecommendationSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    score = serializers.FloatField()
    reason = serializers.CharField(required=False)


class BookRecommendationSerializer(serializers.ModelSerializer):
    score = serializers.FloatField(read_only=True)
    reason = serializers.CharField(read_only=True, required=False)
    
    class Meta:
        model = Book
        fields = ['BookID', 'Title', 'AuthorID', 'CategoryID', 'Price', 'ImageURL', 'score', 'reason']


class RecommendationRequestSerializer(serializers.Serializer):
    recommendation_type = serializers.ChoiceField(
        choices=['collaborative', 'content_based', 'trending', 'hybrid'],
        default='hybrid'
    )
    limit = serializers.IntegerField(default=10, min_value=1, max_value=50)
    category_id = serializers.IntegerField(required=False)
    exclude_books = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
