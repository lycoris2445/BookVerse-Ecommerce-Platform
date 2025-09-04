from django.urls import path
from .views import (
    get_cart, 
    add_to_cart, 
    update_cart_item, 
    remove_from_cart, 
    clear_cart,
    add_item
)

urlpatterns = [
    path('', get_cart, name='get-cart'),
    path('add/', add_to_cart, name='add-to-cart'),  # Legacy URL
    path('items/', add_item, name='add-item'),       # New URL for POST /api/v1/cart/items/
    path('items/<int:book_id>/', update_cart_item, name='update-cart-item'),
    path('items/<int:book_id>/remove/', remove_from_cart, name='remove-from-cart'),
    path('clear/', clear_cart, name='clear-cart'),
]
