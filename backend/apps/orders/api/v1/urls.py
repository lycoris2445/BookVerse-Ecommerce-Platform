from django.urls import path
from .views import create_order, list_orders, get_order, cancel_order, create_order_from_cart
from .cart_views import get_cart, add_to_cart, update_item_qty, remove_item

urlpatterns = [
    path('', create_order, name='create-order'),  # POST to create
    path('from-cart/', create_order_from_cart, name='create-order-from-cart'),  # POST create from cart
    path('list/', list_orders, name='list-orders'),  # GET user orders
    # Cart-as-order endpoints
    path('cart/', get_cart),
    path('cart/items/', add_to_cart),            # POST {book_id|product_id, qty}
    path('cart/items/qty/', update_item_qty),    # PATCH {book_id, qty}
    path('cart/items/<int:book_id>/', remove_item),
    path('<int:order_id>/', get_order, name='get-order'),  # GET order details
    path('<int:order_id>/cancel/', cancel_order, name='cancel-order'),  # PATCH to cancel
]
