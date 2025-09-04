from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from ...models import Customer, User


class RegisterInSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if Customer.objects.filter(Email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        customer = Customer(
            FullName=validated_data['full_name'],
            Email=validated_data['email'],
            Phone=validated_data.get('phone', ''),
            Address=validated_data.get('address', ''),
            PasswordHash=make_password(validated_data['password']),
            CreatedAt=timezone.now()
        )
        customer.save()
        return customer


class LoginInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CustomerOutSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='CustomerID', read_only=True)
    full_name = serializers.CharField(source='FullName')
    email = serializers.EmailField(source='Email')
    phone = serializers.CharField(source='Phone')
    address = serializers.CharField(source='Address')
    created_at = serializers.DateTimeField(source='CreatedAt')

    class Meta:
        model = Customer
        fields = ['id', 'full_name', 'email', 'phone', 'address', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
