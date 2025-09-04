from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from decimal import Decimal

from apps.orders.models import Order, OrderDetail
from apps.catalog.models import Book
from .serializers import (
    CreateOrderSerializer,
    OrderResponseSerializer,
    OrderListSerializer,
    UpdateOrderStatusSerializer
)


# ...existing code...


@extend_schema(
    tags=["orders"],
    request=CreateOrderSerializer,
    responses={201: OrderResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create order from cart by changing status from 'cart' to 'confirmed'"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = CreateOrderSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        if data.get('from_cart', True):
            # Find cart order for user
            try:
                cart_order = Order.objects.get(CustomerID=customer_id, Status='cart')
                
                # Check if cart has items
                cart_items = OrderDetail.objects.filter(OrderID=cart_order.OrderID)
                if not cart_items.exists():
                    return Response(
                        {"error": "Cart is empty"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Update status to confirmed and order date
                cart_order.Status = 'confirmed'
                cart_order.OrderDate = timezone.now()
                cart_order.save()
                
                return Response({"order_id": cart_order.OrderID}, status=status.HTTP_201_CREATED)
                
            except Order.DoesNotExist:
                return Response(
                    {"error": "Cart is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Create order from explicit items (existing logic)
            items_data = data['items']
            if not items_data:
                return Response(
                    {"error": "No valid items to order"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate total and validate stock
            total_amount = Decimal('0.00')
            validated_items = []

            for item in items_data:
                book_data = Book.objects.filter(BookID=item['book_id']).values('BookID', 'Title', 'Price', 'Stock').first()
                if not book_data:
                    return Response(
                        {"error": f"Book with ID {item['book_id']} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                if book_data['Stock'] < item['quantity']:
                    return Response(
                        {"error": f"Not enough stock for {book_data['Title']}. Available: {book_data['Stock']}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                price = item.get('price', book_data['Price'])
                subtotal = price * item['quantity']
                total_amount += subtotal
                validated_items.append({
                    'book_id': item['book_id'],
                    'quantity': item['quantity'],
                    'price': price,
                    'subtotal': subtotal
                })

            # Create the order
            order = Order.objects.create(
                CustomerID=customer_id, 
                TotalAmount=total_amount,
                Status='confirmed',
                OrderDate=timezone.now()
            )
            for item in validated_items:
                OrderDetail.objects.create(
                    OrderID=order.OrderID,
                    BookID=item['book_id'],
                    Quantity=item['quantity'],
                    Price=item['price']
                )

            return Response({"order_id": order.OrderID}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["orders"],
    responses={200: OrderListSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    """List user's orders"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    orders = Order.objects.filter(CustomerID=customer_id).order_by('-OrderDate')
    
    orders_data = []
    for order in orders:
        # Count total items
        total_items = OrderDetail.objects.filter(OrderID=order.OrderID).count()
        
        orders_data.append({
            'order_id': order.OrderID,
            'order_date': order.OrderDate,
            'total_amount': order.TotalAmount,
            'status': order.Status,
            'total_items': total_items
        })
    
    serializer = OrderListSerializer(orders_data, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=["orders"],
    responses={200: OrderResponseSerializer}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    """Get order details"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order = Order.objects.get(OrderID=order_id, CustomerID=customer_id)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get order details
    details = OrderDetail.objects.filter(OrderID=order.OrderID)
    order_items = []
    
    for detail in details:
        # Use values() to get only Title field and avoid missing columns
        book_data = Book.objects.filter(BookID=detail.BookID).values('Title').first()
        book_title = book_data['Title'] if book_data else f"Book ID {detail.BookID}"
        
        order_items.append({
            'order_detail_id': detail.OrderDetailID,
            'book_id': detail.BookID,
            'book_title': book_title,
            'quantity': detail.Quantity,
            'price': detail.Price,
            'subtotal': detail.Price * detail.Quantity
        })
    
    order_data = {
        'order_id': order.OrderID,
        'customer_id': order.CustomerID,
        'order_date': order.OrderDate,
        'total_amount': order.TotalAmount,
        'status': order.Status,
        'items': order_items
    }
    
    serializer = OrderResponseSerializer(order_data)
    return Response(serializer.data)


@extend_schema(
    tags=["orders"],
    request=UpdateOrderStatusSerializer,
    responses={200: OrderResponseSerializer}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order (only if pending/confirmed)"""
    customer_id = getattr(request.user, 'id', None)
    if not customer_id:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        order = Order.objects.get(OrderID=order_id, CustomerID=customer_id)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if order.Status not in ['pending', 'confirmed']:
        return Response(
            {"error": f"Cannot cancel order with status: {order.Status}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    order.Status = 'cancelled'
    order.save()
    
    return Response({"message": "Order cancelled successfully"})


@extend_schema(
    tags=["orders"],
    responses={201: OrderResponseSerializer}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_from_cart(request):
    """Create order from current cart using cart service (Orders table with status='cart')"""
    try:
        from apps.cart.services.cart_service import get_or_create_cart_order
        from django.db import transaction
        
        # Get cart order (status='cart')
        cart_order = get_or_create_cart_order(request)
        cart_items = OrderDetail.objects.filter(OrderID=cart_order)
        
        if not cart_items.exists():
            return Response({
                'status': 'error',
                'message': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # Simply change status from 'cart' to 'confirmed'
            cart_order.Status = 'confirmed'
            cart_order.OrderDate = timezone.now()
            cart_order.save()
        
        return Response({
            'status': 'success',
            'message': 'Order created successfully from cart',
            'order_id': cart_order.OrderID,
            'total_amount': cart_order.TotalAmount
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Failed to create order from cart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
