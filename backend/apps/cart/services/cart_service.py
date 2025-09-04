from django.contrib.auth.models import User
from django.utils import timezone
from apps.orders.models import Order, OrderDetail


def get_or_create_cart_order(request):
    """
    Get or create cart order for current request.
    Cart is stored as Order with status='cart'
    Priority: user cart -> session cart (use CustomerID=0 for anonymous)
    """
    if request.user.is_authenticated:
        # User is logged in, use user-based cart
        cart_order, created = Order.objects.get_or_create(
            CustomerID=request.user.id,
            Status='cart',
            defaults={
                'OrderDate': timezone.now(),
                'TotalAmount': 0
            }
        )
        return cart_order
    else:
        # User not logged in, use CustomerID=0 for anonymous session cart
        cart_order, created = Order.objects.get_or_create(
            CustomerID=0,  # Use 0 for anonymous session users
            Status='cart',
            defaults={
                'OrderDate': timezone.now(),
                'TotalAmount': 0
            }
        )
        return cart_order


def merge_carts_on_login(request, user):
    """
    Merge session cart with user cart when user logs in
    """
    try:
        # Get session cart (anonymous cart with CustomerID=0)
        session_cart = Order.objects.get(
            CustomerID=0,  # Anonymous session cart
            Status='cart'
        )
        
        # Get or create user cart
        user_cart, created = Order.objects.get_or_create(
            CustomerID=user.id,
            Status='cart',
            defaults={
                'OrderDate': timezone.now(),
                'TotalAmount': 0
            }
        )
        
        # Merge cart items (OrderDetails)
        for session_item in OrderDetail.objects.filter(OrderID=session_cart.OrderID):
            # Check if item already exists in user cart
            try:
                user_item = OrderDetail.objects.get(
                    OrderID=user_cart.OrderID,
                    BookID=session_item.BookID
                )
                # If item already exists, add quantities
                user_item.Quantity += session_item.Quantity
                user_item.save()
            except OrderDetail.DoesNotExist:
                # Create new item in user cart
                OrderDetail.objects.create(
                    OrderID=user_cart.OrderID,
                    BookID=session_item.BookID,
                    Quantity=session_item.Quantity,
                    Price=session_item.Price
                )
        
        # Delete session cart after merging
        session_cart.delete()
        
        # Update user cart total
        update_cart_total(user_cart)
        
    except Order.DoesNotExist:
        # No session cart to merge
        pass


def update_cart_total(cart_order):
    """Update cart order total amount"""
    total = sum(
        item.Price * item.Quantity 
        for item in OrderDetail.objects.filter(OrderID=cart_order.OrderID)
    )
    cart_order.TotalAmount = total
    cart_order.save()
    return total
