from rest_framework import serializers


class AddItemIn(serializers.Serializer):
    book_id = serializers.IntegerField(required=False)
    product_id = serializers.IntegerField(required=False)
    qty = serializers.IntegerField(min_value=1, default=1)

    def validate(self, attrs):
        bid = attrs.get("book_id") or attrs.get("product_id")
        if not bid:
            raise serializers.ValidationError({"book_id": "This field is required."})
        attrs["book_id"] = bid
        attrs.pop("product_id", None)
        return attrs


class UpdateQtyIn(serializers.Serializer):
    book_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=0)


class OrderOut(serializers.Serializer):
    order_id = serializers.IntegerField()
    status = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    items = serializers.ListField(child=serializers.DictField())
