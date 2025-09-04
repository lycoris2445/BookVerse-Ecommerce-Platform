from rest_framework import serializers
from django.utils import timezone

ACTION_CHOICES = ("view", "add_to_cart", "checkout", "purchase")

class ActivityIn(serializers.Serializer):
    book_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    activity_time = serializers.DateTimeField(required=False)

    def to_internal_value(self, data):
        v = super().to_internal_value(data)
        # ensure there's always a timestamp
        v["activity_time"] = v.get("activity_time") or timezone.now()
        return v

class ActivityBulkIn(serializers.Serializer):
    events = ActivityIn(many=True)
