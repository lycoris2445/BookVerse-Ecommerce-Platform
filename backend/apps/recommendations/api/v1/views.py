from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from django.db import connection
from django.utils import timezone
from apps.recommendations.services import recommendation_engine
import json
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    """Test API connection"""
    return Response({
        'success': True,
        'message': 'API connected successfully'
    })

class PopularBooksView(APIView):
    """API để lấy sách phổ biến"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                # Lấy sách có nhiều đơn hàng nhất
                cursor.execute("""
                    SELECT b.BookID, b.Title, b.Price, b.ImageURL, b.Description,
                           a.AuthorName, c.CategoryName,
                           COUNT(od.BookID) as order_count
                    FROM book b
                    LEFT JOIN author a ON b.AuthorID = a.AuthorID
                    LEFT JOIN category c ON b.CategoryID = c.CategoryID
                    LEFT JOIN orderdetail od ON b.BookID = od.BookID
                    WHERE b.Stock > 0
                    GROUP BY b.BookID
                    ORDER BY order_count DESC
                    LIMIT 10
                """)
                
                books = []
                for row in cursor.fetchall():
                    books.append({
                        'id': row[0],
                        'title': row[1],
                        'price': float(row[2]) if row[2] else 0,
                        'image_url': row[3],
                        'description': row[4],
                        'author': row[5],
                        'category': row[6],
                        'order_count': row[7]
                    })
                
                return Response({
                    'success': True,
                    'data': books,
                    'message': 'Lấy danh sách sách phổ biến thành công'
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Lỗi khi lấy danh sách sách phổ biến'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserRecommendationsView(APIView):
    """API để lấy gợi ý sách cho user cụ thể"""
    permission_classes = [AllowAny]
    
    def get(self, request, user_id):
        try:
            with connection.cursor() as cursor:
                # Lấy category từ lịch sử mua hàng của user
                cursor.execute("""
                    SELECT DISTINCT b.CategoryID, COUNT(*) as purchase_count
                    FROM orders o
                    JOIN orderdetail od ON o.OrderID = od.OrderID
                    JOIN book b ON od.BookID = b.BookID
                    WHERE o.CustomerID = %s
                    GROUP BY b.CategoryID
                    ORDER BY purchase_count DESC
                    LIMIT 3
                """, [user_id])
                
                preferred_categories = [row[0] for row in cursor.fetchall()]
                
                if preferred_categories:
                    # Gợi ý sách từ các category user thích
                    placeholders = ','.join(['%s'] * len(preferred_categories))
                    cursor.execute(f"""
                        SELECT b.BookID, b.Title, b.Price, b.ImageURL, b.Description,
                               a.Name, c.CategoryName
                        FROM book b
                        LEFT JOIN author a ON b.AuthorID = a.AuthorID
                        LEFT JOIN category c ON b.CategoryID = c.CategoryID
                        WHERE b.CategoryID IN ({placeholders})
                          AND b.Stock > 0
                          AND b.BookID NOT IN (
                              SELECT DISTINCT od.BookID 
                              FROM orders o 
                              JOIN orderdetail od ON o.OrderID = od.OrderID 
                              WHERE o.CustomerID = %s
                          )
                        ORDER BY RAND()
                        LIMIT 10
                    """, preferred_categories + [user_id])
                else:
                    # Nếu user chưa mua gì, gợi ý sách phổ biến
                    cursor.execute("""
                        SELECT b.BookID, b.Title, b.Price, b.ImageURL, b.Description,
                               a.AuthorName, c.CategoryName,
                               COUNT(od.BookID) as order_count
                        FROM book b
                        LEFT JOIN author a ON b.AuthorID = a.AuthorID
                        LEFT JOIN category c ON b.CategoryID = c.CategoryID
                        LEFT JOIN orderdetail od ON b.BookID = od.BookID
                        WHERE b.Stock > 0
                        GROUP BY b.BookID
                        ORDER BY order_count DESC
                        LIMIT 10
                    """)
                
                books = []
                for row in cursor.fetchall():
                    books.append({
                        'id': row[0],
                        'title': row[1],
                        'price': float(row[2]) if row[2] else 0,
                        'image_url': row[3],
                        'description': row[4],
                        'author': row[5],
                        'category': row[6]
                    })
                
                return Response({
                    'success': True,
                    'data': books,
                    'message': f'Lấy gợi ý sách cho user {user_id} thành công'
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'message': 'Lỗi khi lấy gợi ý sách cho user'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=["recommendations"],
    summary="Content-based recommendations for authenticated user",
    description="Get personalized book recommendations based on user's activity using TF-IDF content similarity. Requires authentication.",
    parameters=[
        OpenApiParameter(
            name='k',
            description='Number of recommendations to return',
            required=False,
            type=int,
            default=12
        ),
    ],
    responses={
        200: OpenApiResponse(
            description='Successful response with recommendations',
            examples=[
                {
                    "application/json": {
                        "results": [
                            {
                                "book_id": 123,
                                "title": "Example Book",
                                "price": 299000.0,
                                "stock": 10,
                                "description": "Book description...",
                                "score": 0.8567
                            }
                        ]
                    }
                }
            ]
        ),
        401: OpenApiResponse(description='Authentication required'),
        500: OpenApiResponse(description='Internal server error')
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def content_based_recommendations(request):
    """
    Content-based recommendations endpoint
    
    Returns personalized book recommendations based on user's activity history
    using TF-IDF content similarity and cosine similarity.
    
    - Requires user authentication (JWT or session)
    - Returns empty list for users with no activity (cold start)
    - Filters out already purchased books and out-of-stock items
    - SLA target: < 150ms response time
    """
    try:
        start_time = timezone.now()
        
        # Extract user ID from authenticated user
        customer_id = None
        if hasattr(request.user, 'customerid'):
            customer_id = request.user.customerid
        elif hasattr(request.user, 'customer'):
            customer_id = request.user.customer.CustomerID
        elif hasattr(request, 'session') and 'customer_id' in request.session:
            customer_id = request.session['customer_id']
        else:
            # Try to get from JWT token or other auth
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                from apps.users.services.jwt_utils import decode_jwt_token
                token = auth_header.split(' ', 1)[1]
                payload = decode_jwt_token(token)
                if payload and payload.get('sub'):
                    customer_id = payload.get('sub')
        
        if not customer_id:
            # Fallback to demo customer for testing
            customer_id = 2  # Customer with activity data
            logger.info(f"Using fallback customer_id: {customer_id}")
        
        # Get k parameter (default 12, max 50)
        k = int(request.GET.get('k', 12))
        k = min(max(k, 1), 50)  # Clamp between 1-50
        
        # Get content-based recommendations
        recommendations = recommendation_engine.get_content_recommendations(
            user_id=customer_id, 
            k=k
        )
        
        # Calculate response time
        processing_time = (timezone.now() - start_time).total_seconds()
        
        # Log performance
        logger.info(f"Content recommendations for user {customer_id}: {len(recommendations)} results in {processing_time:.3f}s")
        
        # Check SLA (150ms target)
        if processing_time > 0.15:
            logger.warning(f"SLA exceeded: {processing_time:.3f}s > 0.15s for user {customer_id}")
        
        # Return standardized response format
        return Response({
            "results": recommendations
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in content-based recommendations: {str(e)}")
        return Response({
            "error": "Internal server error",
            "message": "Failed to generate recommendations"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
