from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal
import logging

from apps.cart.services.cart_service import get_or_create_cart_order, update_cart_total
from apps.orders.models import Order, OrderDetail
from apps.catalog.models import Book
from .serializers import CartItemSerializer, CartResponseSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cart(request):
    """Get current cart contents from Orders table (status='cart')"""
    try:
        cart_order = get_or_create_cart_order(request)
        cart_items = OrderDetail.objects.filter(OrderID=cart_order.OrderID)
        
        items_data = []
        total_amount = Decimal('0.00')
        total_items = 0
        
        for cart_item in cart_items:
            # Get book info
            try:
                book = Book.objects.get(BookID=cart_item.BookID)
                subtotal = cart_item.Price * cart_item.Quantity
                items_data.append({
                    'book_id': cart_item.BookID,
                    'title': book.Title,
                    'price': cart_item.Price,
                    'quantity': cart_item.Quantity,
                    'subtotal': subtotal
                })
                total_amount += subtotal
                total_items += cart_item.Quantity
            except Book.DoesNotExist:
                continue  # Skip items with missing books
        
        return Response({
            'status': 'success',
            'items': items_data,
            'total_items': total_items,
            'total_amount': total_amount
        })
    
    except Exception as e:
        logger.error(f"Error getting cart: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error getting cart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_to_cart(request):
    """Add item to cart - stores in Orders table with status='cart'"""
    try:
        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        # Get book
        try:
            book = Book.objects.get(BookID=book_id)
        except Book.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Book not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create cart order
        cart_order = get_or_create_cart_order(request)
        
        with transaction.atomic():
            # Get or create cart item (OrderDetail)
            try:
                cart_item = OrderDetail.objects.get(
                    OrderID=cart_order.OrderID,
                    BookID=book_id
                )
                # Item already exists, increase quantity
                cart_item.Quantity += quantity
                cart_item.save()
            except OrderDetail.DoesNotExist:
                # Create new cart item
                cart_item = OrderDetail.objects.create(
                    OrderID=cart_order.OrderID,
                    BookID=book_id,
                    Quantity=quantity,
                    Price=book.Price
                )
            
            # Update cart total
            update_cart_total(cart_order)
        
        return Response({
            'status': 'success',
            'message': 'Item added to cart successfully',
            'book_id': book_id,
            'quantity': cart_item.Quantity
        })
        
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return Response({
            'status': 'error', 
            'message': f'Failed to add to cart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([AllowAny])
def update_cart_item(request, book_id):
    """Update cart item quantity in Orders table"""
    try:
        quantity = request.data.get('quantity', 1)
        if quantity < 1:
            return Response({
                'status': 'error',
                'message': 'Quantity must be at least 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart_order = get_or_create_cart_order(request)
        
        try:
            cart_item = OrderDetail.objects.get(OrderID=cart_order.OrderID, BookID=book_id)
            cart_item.Quantity = quantity
            cart_item.save()
            
            # Update cart total
            update_cart_total(cart_order)
            
            return Response({
                'status': 'success',
                'message': 'Cart item updated successfully',
                'book_id': book_id,
                'quantity': quantity
            })
        except OrderDetail.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error updating cart item: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error updating cart item: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def remove_from_cart(request, book_id):
    """Remove item from cart (Orders table)"""
    try:
        cart_order = get_or_create_cart_order(request)
        
        try:
            cart_item = OrderDetail.objects.get(OrderID=cart_order.OrderID, BookID=book_id)
            cart_item.delete()
            
            # Update cart total
            update_cart_total(cart_order)
            
            return Response({
                'status': 'success',
                'message': 'Item removed from cart successfully',
                'book_id': book_id
            })
        except OrderDetail.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Item not found in cart'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error removing from cart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def clear_cart(request):
    """Clear all items from cart (Orders table)"""
    try:
        cart_order = get_or_create_cart_order(request)
        deleted_count = OrderDetail.objects.filter(OrderID=cart_order.OrderID).delete()[0]
        
        # Update cart total to 0
        cart_order.TotalAmount = 0
        cart_order.save()
        
        return Response({
            'status': 'success',
            'message': f'Cart cleared successfully. {deleted_count} items removed.'
        })
        
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return Response({
            'status': 'error',
            'message': f'Error clearing cart: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Alias for add_to_cart to support both URLs
add_item = add_to_cart
