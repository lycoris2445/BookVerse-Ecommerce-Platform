import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.catalog.models import Book

User = get_user_model()

@pytest.mark.django_db
def test_jwt_cart_order_flow():
    user = User.objects.create_user(username='jwtuser', password='testpass')
    book = Book.objects.create(BookID=1, Title='Book 1', Price=100, Stock=10)
    client = APIClient()
    # Login and get JWT token
    response = client.post('/api/v1/users/login/', {'username': 'jwtuser', 'password': 'testpass'})
    token = response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    # Add to cart
    response = client.post('/api/v1/cart/add/', {'book_id': book.BookID, 'quantity': 2})
    assert response.status_code == 200
    # Get cart
    response = client.get('/api/v1/cart/')
    assert response.status_code == 200
    assert response.data['total_items'] == 2
    # Create order from cart
    response = client.post('/api/v1/orders/', {'from_cart': True})
    assert response.status_code == 201
    # Cart should be empty
    response = client.get('/api/v1/cart/')
    assert response.data['total_items'] == 0

@pytest.mark.django_db
def test_session_cart_order_flow():
    book = Book.objects.create(BookID=2, Title='Book 2', Price=200, Stock=10)
    client = APIClient()
    # Add to cart (session)
    response = client.post('/api/v1/cart/add/', {'book_id': book.BookID, 'quantity': 1})
    assert response.status_code == 200
    # Get cart
    response = client.get('/api/v1/cart/')
    assert response.status_code == 200
    assert response.data['total_items'] == 1
    # Create order from cart
    response = client.post('/api/v1/orders/', {'from_cart': True})
    assert response.status_code == 201
    # Cart should be empty
    response = client.get('/api/v1/cart/')
    assert response.data['total_items'] == 0
