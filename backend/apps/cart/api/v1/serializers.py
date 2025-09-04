from rest_framework import serializers
from apps.catalog.models import Book


class CartItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)  # Accept both product_id and book_id
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    def validate(self, data):
        # Map product_id to book_id if provided
        if 'product_id' in data and 'book_id' not in data:
            data['book_id'] = data['product_id']
        elif 'book_id' not in data and 'product_id' not in data:
            raise serializers.ValidationError("Either book_id or product_id is required")
        
        # Remove product_id after mapping
        if 'product_id' in data:
            data.pop('product_id')
            
        return data
    
    def validate_book_id(self, value):
        # Use a lightweight existence check to avoid selecting all columns (some DBs may have missing columns)
        if not Book.objects.filter(BookID=value).exists():
            raise serializers.ValidationError("Book not found")
        return value


class CartItemResponseSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    title = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class CartResponseSerializer(serializers.Serializer):
    items = CartItemResponseSerializer(many=True)
    total_items = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)



class AddToCartSerializer(serializers.Serializer):
    book_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        # Accept either book_id or product_id, map product_id to book_id
        book_id = data.get('book_id')
        product_id = data.get('product_id')
        if book_id is None and product_id is not None:
            data['book_id'] = product_id
        elif book_id is None and product_id is None:
            raise serializers.ValidationError("Either book_id or product_id is required.")
        return data

    def validate_book_id(self, value):
        stock = Book.objects.filter(BookID=value).values_list('Stock', flat=True).first()
        if stock is None:
            raise serializers.ValidationError("Book not found")
        if stock < 1:
            raise serializers.ValidationError("Book out of stock")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)  # 0 means remove
