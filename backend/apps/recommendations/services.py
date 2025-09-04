"""
Content-based Recommendation Engine using TF-IDF
Dựa trên dữ liệu tracking của user để gợi ý sách tương tự với TF-IDF và cosine similarity
"""
from django.db import connection
from django.utils import timezone
from django.conf import settings
from collections import defaultdict, Counter
from functools import lru_cache
import re
import math
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_absolute_image_url(image_path, request=None):
    """Convert relative image path to absolute URL"""
    if not image_path:
        return ''
    if image_path.startswith(('http://', 'https://')):
        return image_path
    
    # Try to get base URL from Django settings or request
    from django.conf import settings
    
    # Use BACKEND_URL from environment if set, otherwise construct from request
    base_url = getattr(settings, 'BACKEND_URL', None)
    if not base_url:
        if request:
            base_url = f"{request.scheme}://{request.get_host()}"
        else:
            # Fallback for local development
            base_url = "http://127.0.0.1:8000"
    
    if image_path.startswith('/'):
        return f"{base_url}{image_path}"
    return f"{base_url}/media/{image_path}"

class ContentBasedRecommendationEngine:
    """
    Content-based recommendation engine sử dụng TF-IDF và cosine similarity
    - Build TF-IDF matrix từ content (Title + Description + CategoryName + AuthorName + PublisherName)
    - Tạo user profile từ weighted activities với recency decay
    - Tính cosine similarity giữa user profile và item vectors
    """
    
    def __init__(self):
        self.tfidf_matrix = None
        self.book_id_mapping = {}  # book_id -> matrix_index
        self.reverse_mapping = {}  # matrix_index -> book_id
        self.tfidf_vectorizer = None
        self.last_build_time = None
        
    @lru_cache(maxsize=128)  # Giảm cache size
    def get_books_content_data(self):
        """Lấy dữ liệu content của tất cả sách để build TF-IDF (memory optimized)"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT b.BookID, b.Title, b.Description, 
                       c.CategoryName, a.Name as AuthorName, p.Name as PublisherName
                FROM book b
                LEFT JOIN category c ON b.CategoryID = c.CategoryID
                LEFT JOIN author a ON b.AuthorID = a.AuthorID  
                LEFT JOIN publisher p ON b.PublisherID = p.PublisherID
                WHERE b.Stock > 0
                ORDER BY b.BookID
                LIMIT 1000
            """)  # Giới hạn số lượng books để tránh memory overflow
            
            books_data = []
            book_ids = []
            
            for row in cursor.fetchall():
                book_id, title, description, category_name, author_name, publisher_name = row
                
                # Tạo text content từ các trường (tối ưu memory)
                content_parts = []
                if title:
                    content_parts.append(title[:100])  # Giới hạn title length
                if description:
                    content_parts.append(description[:200])  # Giới hạn description
                if category_name:
                    content_parts.append(category_name)
                if author_name:
                    content_parts.append(author_name)
                if publisher_name:
                    content_parts.append(publisher_name)
                
                content_text = ' '.join(content_parts)
                books_data.append(content_text)
                book_ids.append(book_id)
            
            return books_data, book_ids
    
    def build_tfidf_matrix(self, max_features=5000):
        """Build TF-IDF matrix cho tất cả sách (memory-optimized, pure Python)"""
        try:
            logger.info("Building memory-optimized TF-IDF matrix...")
            start_time = timezone.now()
            
            books_content, book_ids = self.get_books_content_data()
            
            if not books_content:
                logger.warning("No books found for TF-IDF matrix")
                return False
            
            # Tokenize và preprocessing (memory efficient)
            documents = []
            vocabulary = set()
            
            for content in books_content:
                # Đơn giản: lowercase, split by space, remove special chars
                tokens = re.findall(r'\b\w+\b', content.lower())
                # Giới hạn tokens per document để tránh memory spike
                tokens = tokens[:50] if len(tokens) > 50 else tokens
                
                # Tạo 1-gram (skip 2-gram để tiết kiệm memory)
                doc_tokens = tokens[:]
                
                documents.append(doc_tokens)
                vocabulary.update(doc_tokens)
                
                # Memory safety: giới hạn vocabulary size
                if len(vocabulary) > max_features * 2:
                    break
            
            # Lọc từ có tần số thấp (min_df=2) và giới hạn vocabulary
            term_doc_freq = Counter()
            for doc in documents:
                unique_terms = set(doc)
                for term in unique_terms:
                    term_doc_freq[term] += 1
            
            # Chọn top terms để giới hạn memory
            vocabulary = [term for term, freq in term_doc_freq.most_common(max_features) if freq >= 2]
            
            if not vocabulary:
                logger.warning("No valid vocabulary after filtering")
                return False
            
            logger.info(f"Vocabulary size: {len(vocabulary)} terms")
            
            # Tính TF-IDF matrix (memory efficient - process by chunks)
            tfidf_matrix = []
            num_docs = len(documents)
            
            for doc_idx, doc_tokens in enumerate(documents):
                if doc_idx % 100 == 0:
                    logger.debug(f"Processing document {doc_idx}/{num_docs}")
                
                doc_vector = []
                term_freq = Counter(doc_tokens)
                
                for term in vocabulary:
                    tf = term_freq.get(term, 0) / len(doc_tokens) if doc_tokens else 0
                    df = term_doc_freq.get(term, 0)
                    idf = math.log(num_docs / (df + 1)) if df > 0 else 0
                    tfidf = tf * idf
                    doc_vector.append(tfidf)
                
                # L2 normalization
                norm = math.sqrt(sum(x * x for x in doc_vector))
                if norm > 0:
                    doc_vector = [x / norm for x in doc_vector]
                
                tfidf_matrix.append(doc_vector)
            
            self.tfidf_matrix = tfidf_matrix
            self.vocabulary = vocabulary
            
            # Tạo mapping
            self.book_id_mapping = {book_id: idx for idx, book_id in enumerate(book_ids)}
            self.reverse_mapping = {idx: book_id for idx, book_id in enumerate(book_ids)}
            
            self.last_build_time = timezone.now()
            build_duration = (self.last_build_time - start_time).total_seconds()
            
            logger.info(f"Memory-optimized TF-IDF matrix built in {build_duration:.2f}s")
            logger.info(f"Matrix shape: {len(tfidf_matrix)}x{len(vocabulary)}, Books: {len(book_ids)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error building TF-IDF matrix: {str(e)}")
            return False
        
    def get_user_activity_with_recency(self, user_id, days=30):
        """Lấy dữ liệu activity của user với recency decay"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT BookID, Action, ActivityTime, COUNT(*) as frequency
                FROM useractivity
                WHERE CustomerID = %s AND ActivityTime >= %s
                GROUP BY BookID, Action, ActivityTime
                ORDER BY ActivityTime DESC
            """, [user_id, cutoff_date])
            
            activities = []
            for row in cursor.fetchall():
                book_id, action, activity_time, frequency = row
                
                # Tính recency decay (30 ngày = weight 1.0, giảm dần)
                # Convert naive datetime to timezone-aware
                if activity_time.tzinfo is None:
                    activity_time = timezone.make_aware(activity_time)
                days_ago = (timezone.now() - activity_time).days
                recency_weight = max(0.1, 1.0 - (days_ago / days))
                
                # Trọng số hành vi: view=1, add_to_cart=3, purchase=5
                action_weights = {
                    'view': 1,
                    'click': 1,
                    'add_to_cart': 3,
                    'add_cart': 3,  # alias
                    'checkout': 4,
                    'purchase': 5
                }
                
                action_weight = action_weights.get(action.lower(), 1)
                final_weight = frequency * action_weight * recency_weight
                
                activities.append({
                    'book_id': book_id,
                    'action': action,
                    'weight': final_weight
                })
            
            return activities
    
    def compute_user_profile_vector(self, user_id):
        """Tính user profile vector từ weighted activities và TF-IDF matrix"""
        if not self.tfidf_matrix or not self.book_id_mapping:
            logger.warning("TF-IDF matrix not built yet")
            return None
        
        activities = self.get_user_activity_with_recency(user_id)
        if not activities:
            return None
        
        # Tạo user profile vector = weighted sum of item vectors
        vocab_size = len(self.vocabulary)
        user_vector = [0.0] * vocab_size
        total_weight = 0.0
        
        for activity in activities:
            book_id = activity['book_id']
            weight = activity['weight']
            
            if book_id in self.book_id_mapping:
                matrix_idx = self.book_id_mapping[book_id]
                book_vector = self.tfidf_matrix[matrix_idx]
                
                # Add weighted book vector to user profile
                for i in range(vocab_size):
                    user_vector[i] += book_vector[i] * weight
                total_weight += weight
        
        if total_weight == 0:
            return None
        
        # Normalize user vector
        for i in range(vocab_size):
            user_vector[i] /= total_weight
        
        # L2 normalization
        norm = math.sqrt(sum(x * x for x in user_vector))
        if norm > 0:
            user_vector = [x / norm for x in user_vector]
        
        return user_vector
    
    def cosine_similarity(self, vec1, vec2):
        """Tính cosine similarity giữa 2 vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        return dot_product  # Vì đã normalized nên dot product = cosine similarity
    
    def get_purchased_books(self, user_id):
        """Lấy danh sách sách user đã mua để loại bỏ"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT od.BookID
                FROM orders o
                JOIN orderdetail od ON o.OrderID = od.OrderID  
                WHERE o.CustomerID = %s AND o.Status = 'confirmed'
            """, [user_id])
            
            return {row[0] for row in cursor.fetchall()}
    
    def get_content_recommendations(self, user_id, k=12):
        """Lấy content-based recommendations cho user"""
        try:
            start_time = timezone.now()
            
            # Kiểm tra TF-IDF matrix đã được build chưa
            if not self.tfidf_matrix or not self.book_id_mapping:
                if not self.build_tfidf_matrix():
                    return []
            
            # Tính user profile vector
            user_vector = self.compute_user_profile_vector(user_id)
            if user_vector is None:
                # Cold start: user mới, không có activity
                return []
            
            # Lấy sách đã mua để loại bỏ
            purchased_books = self.get_purchased_books(user_id)
            
            # Tính similarity scores với tất cả sách
            scores = []
            for book_id, matrix_idx in self.book_id_mapping.items():
                # Skip sách đã mua
                if book_id in purchased_books:
                    continue
                
                book_vector = self.tfidf_matrix[matrix_idx]
                similarity = self.cosine_similarity(user_vector, book_vector)
                scores.append((book_id, similarity))
            
            # Sort by similarity descending và lấy top-k
            scores.sort(key=lambda x: x[1], reverse=True)
            top_book_ids = [book_id for book_id, _ in scores[:k]]
            
            # Lấy thông tin chi tiết sách với hình ảnh và tác giả
            if not top_book_ids:
                return []

            placeholders = ','.join(['%s'] * len(top_book_ids))
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT b.BookID, b.Title, b.Price, b.Stock, b.Description, 
                           b.ImageURL, b.ISBN, b.Year,
                           a.Name as AuthorName, c.CategoryName, p.Name as PublisherName
                    FROM book b
                    LEFT JOIN author a ON b.AuthorID = a.AuthorID
                    LEFT JOIN category c ON b.CategoryID = c.CategoryID  
                    LEFT JOIN publisher p ON b.PublisherID = p.PublisherID
                    WHERE b.BookID IN ({placeholders}) AND b.Stock > 0
                    ORDER BY FIELD(b.BookID, {placeholders})
                """, top_book_ids + top_book_ids)
                
                recommendations = []
                score_dict = dict(scores)
                
                for row in cursor.fetchall():
                    book_id, title, price, stock, description, image_url, isbn, year, author_name, category_name, publisher_name = row
                    recommendations.append({
                        'book_id': book_id,
                        'title': title,
                        'author': author_name or 'Unknown Author',
                        'category': category_name or 'Uncategorized', 
                        'publisher': publisher_name or 'Unknown Publisher',
                        'price': float(price) if price else 0.0,
                        'stock': stock or 0,
                        'description': description or '',
                        'image_url': get_absolute_image_url(image_url),
                        'isbn': isbn or '',
                        'year': year,
                        'score': round(score_dict.get(book_id, 0.0), 4)
                    })
            
            processing_time = (timezone.now() - start_time).total_seconds()
            logger.info(f"Content recommendations for user {user_id}: {len(recommendations)} items in {processing_time:.3f}s")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting content recommendations for user {user_id}: {str(e)}")
            return []


    def clear_cache(self):
        """Clear all cached data và artifacts"""
        self.tfidf_matrix = None
        self.book_id_mapping = {}
        self.reverse_mapping = {}
        self.vocabulary = []
        self.last_build_time = None
        
        # Clear LRU cache
        if hasattr(self.get_books_content_data, 'cache_clear'):
            self.get_books_content_data.cache_clear()
    
    def get_build_info(self):
        """Lấy thông tin build hiện tại"""
        if not self.tfidf_matrix:
            return {
                'status': 'not_built',
                'message': 'TF-IDF matrix has not been built yet'
            }
        
        return {
            'status': 'ready',
            'build_time': self.last_build_time,
            'matrix_shape': f"{len(self.tfidf_matrix)}x{len(self.vocabulary)}",
            'num_books': len(self.book_id_mapping),
            'vocabulary_size': len(self.vocabulary),
            'message': 'TF-IDF matrix is ready for recommendations'
        }


    def clear_cache_and_memory(self):
        """Clear all cached data và giải phóng memory"""
        try:
            # Clear TF-IDF data
            self.tfidf_matrix = None
            self.book_id_mapping = {}
            self.reverse_mapping = {}
            self.vocabulary = []
            self.last_build_time = None
            
            # Clear method cache
            self.get_books_content_data.cache_clear()
            
            # Force garbage collection
            import gc
            gc.collect()
            
            logger.info("Cache and memory cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False
    
    def get_memory_usage_info(self):
        """Lấy thông tin memory usage của recommendation engine"""
        info = {
            'tfidf_matrix_loaded': self.tfidf_matrix is not None,
            'vocabulary_size': len(self.vocabulary) if hasattr(self, 'vocabulary') else 0,
            'books_mapped': len(self.book_id_mapping),
            'last_build_time': self.last_build_time.isoformat() if self.last_build_time else None,
            'cache_info': self.get_books_content_data.cache_info()._asdict()
        }
        
        # Estimate memory usage
        if self.tfidf_matrix:
            matrix_size = len(self.tfidf_matrix) * len(self.tfidf_matrix[0]) * 8  # 8 bytes per float
            info['estimated_matrix_memory_mb'] = round(matrix_size / (1024 * 1024), 2)
        else:
            info['estimated_matrix_memory_mb'] = 0
            
        return info


# Singleton instance
recommendation_engine = ContentBasedRecommendationEngine()
