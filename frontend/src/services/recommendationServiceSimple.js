import ApiService from './api';

class RecommendationService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 
      (process.env.NODE_ENV === 'production' 
        ? 'https://ecomtech.onrender.com/api/v1' 
        : 'http://localhost:8000/api/v1');
  }

  /**
   * Lấy gợi ý sách cho customer (sử dụng các bảng có sẵn)
   */
  async getRecommendations(customerId, limit = 10) {
    try {
      const response = await ApiService.request(`/recommendations/v1/recommendations/${customerId}/?limit=${limit}`, {
        method: 'GET',
        auth: false
      });
      return response;
    } catch (error) {
      console.error('Error getting recommendations:', error);
      throw error;
    }
  }

  /**
   * Lấy sách trending
   */
  async getTrendingBooks(days = 7, limit = 10) {
    try {
      const response = await ApiService.request(`/recommendations/v1/trending/?days=${days}&limit=${limit}`, {
        method: 'GET',
        auth: false
      });
      return response;
    } catch (error) {
      console.error('Error getting trending books:', error);
      throw error;
    }
  }

  /**
   * Ghi log hoạt động user
   */
  async logActivity(customerId, bookId, action, sessionId = null) {
    try {
      const data = {
        customer_id: customerId,
        book_id: bookId,
        action: action,
        session_id: sessionId || this.getSessionId()
      };

      const response = await ApiService.request('/recommendations/v1/activity/log/', {
        method: 'POST',
        body: JSON.stringify(data)
      });

      return response;
    } catch (error) {
      console.error('Error logging activity:', error);
      throw error;
    }
  }

  /**
   * Lấy lịch sử hoạt động user
   */
  async getUserActivity(customerId, days = 30) {
    try {
      const response = await ApiService.request(`/recommendations/v1/activity/${customerId}/?days=${days}`, {
        method: 'GET',
        auth: false
      });
      return response;
    } catch (error) {
      console.error('Error getting user activity:', error);
      throw error;
    }
  }

  /**
   * Track các hành vi cơ bản
   */
  async trackView(customerId, bookId) {
    return this.logActivity(customerId, bookId, 'view');
  }

  async trackClick(customerId, bookId) {
    return this.logActivity(customerId, bookId, 'click');
  }

  async trackSearch(customerId, query, bookId = null) {
    return this.logActivity(customerId, bookId || 0, 'search');
  }

  async trackAddToCart(customerId, bookId) {
    return this.logActivity(customerId, bookId, 'add_cart');
  }

  async trackPurchase(customerId, bookId) {
    return this.logActivity(customerId, bookId, 'purchase');
  }

  /**
   * Lấy session ID từ browser
   */
  getSessionId() {
    let sessionId = localStorage.getItem('session_id');
    if (!sessionId) {
      sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      localStorage.setItem('session_id', sessionId);
    }
    return sessionId;
  }

  // Compatibility methods với code cũ
  async getSimilarProducts(productId, limit = 8) {
    // Map product to book và sử dụng trending làm fallback
    return await this.getTrendingBooks(7, limit);
  }

  async getTrendingProducts(limit = 10) {
    return await this.getTrendingBooks(7, limit);
  }

  async getPopularProducts(category = null, limit = 10) {
    return await this.getTrendingBooks(30, limit);
  }
}

export default new RecommendationService();
