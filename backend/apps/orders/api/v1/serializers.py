from rest_framework import serializers
from apps.orders.models import Order, OrderDetail
from apps.catalog.models import Book


class OrderItemSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class CreateOrderSerializer(serializers.Serializer):
    """Create order from cart or explicit items"""
    from_cart = serializers.BooleanField(default=True)
    items = OrderItemSerializer(many=True, required=False)
    shipping_address = serializers.CharField(max_length=500, required=False)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    
    def validate(self, data):
        if not data.get('from_cart') and not data.get('items'):
            raise serializers.ValidationError(
                "Either set from_cart=true or provide items list"
            )
        return data


class OrderDetailResponseSerializer(serializers.Serializer):
    order_detail_id = serializers.IntegerField()
    book_id = serializers.IntegerField()
    book_title = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)


class OrderResponseSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    order_date = serializers.DateTimeField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    items = OrderDetailResponseSerializer(many=True)


class OrderListSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    order_date = serializers.DateTimeField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    total_items = serializers.IntegerField()


class UpdateOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('processing', 'Processing'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled')
        ]
    )
