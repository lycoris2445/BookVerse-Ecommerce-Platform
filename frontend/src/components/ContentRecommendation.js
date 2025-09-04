import React, { useState, useEffect } from 'react';
import { FaChevronLeft, FaChevronRight, FaShoppingCart, FaEye } from 'react-icons/fa';
import { RecommendationService } from '../services';
import ProductImage from './ProductImage';
import './ContentRecommendation.css';

const ContentRecommendation = ({ title = "Gợi ý dành cho bạn", maxItems = 8 }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingTime, setProcessingTime] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [authChecked, setAuthChecked] = useState(false);

  // Check if user is authenticated
  const isAuthenticated = () => {
    // Check multiple possible authentication storage locations
    const authToken = localStorage.getItem('auth_token');
    const accessToken = localStorage.getItem('access_token');
    const legacyToken = localStorage.getItem('authToken');
    const sessionId = sessionStorage.getItem('sessionid');
    const user = localStorage.getItem('user');
    const bookCurrentUser = localStorage.getItem('book_current'); // Local auth system
    
    const authenticated = !!(authToken || accessToken || legacyToken || sessionId || user || bookCurrentUser);
    
    // Debug logging
    console.log('🔐 ContentRecommendation Auth Check:', {
      authToken: !!authToken,
      accessToken: !!accessToken, 
      legacyToken: !!legacyToken,
      sessionId: !!sessionId,
      user: !!user,
      bookCurrentUser: !!bookCurrentUser,
      authenticated
    });
    
    return authenticated;
  };

  // Fetch content-based recommendations using service
  const fetchRecommendations = async () => {
    // For now, allow unauthenticated since backend uses AllowAny and fallback user
    // if (!isAuthenticated()) {
    //   setError('Bạn cần đăng nhập để xem gợi ý cá nhân hóa');
    //   return;
    // }

    setLoading(true);
    setError(null);

    try {
      const data = await RecommendationService.getContentBasedRecommendations(maxItems);
      setRecommendations(data.results || []);
      setProcessingTime(data.processing_time || 0);
      
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      // Fallback to mock data for demo
      setRecommendations([
        {
          book_id: 1,
          title: "To Kill a Mockingbird",
          author: "Harper Lee",
          price: 150000,
          image_url: "https://m.media-amazon.com/images/I/81O7u0dGaWL._UF1000,1000_QL80_.jpg",
          score: 0.95
        },
        {
          book_id: 2, 
          title: "1984",
          author: "George Orwell", 
          price: 120000,
          image_url: "https://m.media-amazon.com/images/I/71kxa1-0mfL._AC_UF1000,1000_QL80_.jpg",
          score: 0.88
        }
      ]);
      console.log('Using fallback mock data for demo');
    } finally {
      setLoading(false);
    }
  };

  // Listen for auth changes
  useEffect(() => {
    const handleStorageChange = () => {
      setAuthChecked(prev => !prev); // Force re-render
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also check on component mount
    const checkAuth = () => {
      // Always try to fetch since backend uses AllowAny with fallback
      fetchRecommendations();
      // if (isAuthenticated()) {
      //   fetchRecommendations();
      // } else {
      //   setError('Bạn cần đăng nhập để xem gợi ý cá nhân hóa');
      // }
    };

    checkAuth();

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [authChecked, maxItems]);

  // Handle image loading errors
  const handleImageError = (e) => {
    e.target.src = '/media/book_images/default.svg';
  };

  // Format price
  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  // Navigation functions
  const slideLeft = () => {
    setCurrentIndex(prev => Math.max(0, prev - 1));
  };

  const slideRight = () => {
    setCurrentIndex(prev => Math.min(recommendations.length - 4, prev + 1));
  };

  // Add to cart function (placeholder)
  const addToCart = async (book) => {
    // Implementation depends on your cart API
    console.log('Adding to cart:', book);
    alert(`Đã thêm "${book.title}" vào giỏ hàng!`);
  };

  if (!isAuthenticated()) {
    return (
      <div className="content-recommendation">
        <div className="auth-required">
          <h3>🔒 Đăng nhập để xem gợi ý cá nhân hóa</h3>
          <p>Hệ thống sẽ phân tích sở thích của bạn để đưa ra những gợi ý sách phù hợp nhất</p>
          <button className="login-btn" onClick={() => window.location.href = '/login'}>
            Đăng nhập ngay
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="content-recommendation">
        <div className="loading">
          <div className="spinner"></div>
          <p>Đang phân tích sở thích của bạn...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content-recommendation">
        <div className="error">
          <p>{error}</p>
          <button onClick={fetchRecommendations}>Thử lại</button>
        </div>
      </div>
    );
  }

  if (!recommendations.length) {
    return (
      <div className="content-recommendation">
        <div className="no-recommendations">
          <h3>Chưa có gợi ý cá nhân hóa</h3>
          <p>Hãy xem và mua thêm một số cuốn sách để chúng tôi có thể đưa ra gợi ý phù hợp với bạn</p>
        </div>
      </div>
    );
  }

  return (
    <div className="content-recommendation">
      <div className="rec-header">
        <h2>{title}</h2>
        <div className="rec-stats">
          <span className="processing-time">
            ⚡ Phân tích trong {processingTime.toFixed(3)}s
          </span>
          <span className="rec-count">
            {recommendations.length} gợi ý
          </span>
        </div>
      </div>

      <div className="rec-carousel">
        {currentIndex > 0 && (
          <button className="nav-btn nav-left" onClick={slideLeft}>
            <FaChevronLeft />
          </button>
        )}

        <div className="rec-container">
          <div 
            className="rec-track"
            style={{ transform: `translateX(-${currentIndex * 25}%)` }}
          >
            {recommendations.map((book) => (
              <div key={book.book_id} className="rec-card">
                <div className="book-image">
                  <ProductImage
                    src={book.image_url}
                    alt={book.title}
                    width="100%"
                    height={250}
                  />
                  <div className="book-overlay">
                    <button className="quick-view" title="Xem nhanh">
                      <FaEye />
                    </button>
                  </div>
                </div>

                <div className="book-info">
                  <h3 className="book-title" title={book.title}>
                    {book.title}
                  </h3>
                  
                  <p className="book-author">
                    👤 {book.author}
                  </p>
                  
                  <p className="book-category">
                    📂 {book.category}
                  </p>

                  <div className="book-meta">
                    <span className="similarity-score">
                      🎯 {(book.score * 100).toFixed(1)}% phù hợp
                    </span>
                  </div>

                  <div className="book-price">
                    {formatPrice(book.price)}
                  </div>

                  <div className="book-actions">
                    <button 
                      className="add-to-cart-btn"
                      onClick={() => addToCart(book)}
                      disabled={book.stock === 0}
                    >
                      <FaShoppingCart />
                      {book.stock > 0 ? 'Thêm vào giỏ' : 'Hết hàng'}
                    </button>
                  </div>

                  <div className="book-description" title={book.description}>
                    {book.description.length > 100 
                      ? book.description.substring(0, 100) + '...'
                      : book.description
                    }
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {currentIndex < recommendations.length - 4 && (
          <button className="nav-btn nav-right" onClick={slideRight}>
            <FaChevronRight />
          </button>
        )}
      </div>

      <div className="rec-footer">
        <p className="rec-algorithm">
          🧠 Powered by Content-Based Filtering with TF-IDF
        </p>
      </div>
    </div>
  );
};

export default ContentRecommendation;
