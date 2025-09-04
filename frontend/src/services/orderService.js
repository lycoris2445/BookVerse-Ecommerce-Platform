import ApiService from './api';

class OrderService {
  // Tạo đơn hàng mới
  async createOrder(orderData) {
    try {
      const response = await ApiService.request('/api/v1/orders/', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });
      
      return response;
    } catch (error) {
      console.error('Create order failed:', error);
      throw error;
    }
  }

  // Tạo đơn hàng từ giỏ hàng
  async createOrderFromCart(orderData = {}) {
    try {
      const response = await ApiService.request('/api/v1/orders/from-cart/', {
        method: 'POST',
        body: JSON.stringify(orderData)
      });
      
      return response;
    } catch (error) {
      console.error('Create order from cart failed:', error);
      throw error;
    }
  }

  // Lấy danh sách đơn hàng của user
  async getUserOrders(params = {}) {
    try {
      const queryParams = new URLSearchParams();
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          queryParams.append(key, params[key]);
        }
      });
      
      const queryString = queryParams.toString();
      const endpoint = `/api/v1/orders/list/${queryString ? `?${queryString}` : ''}`;
      
      return await ApiService.request(endpoint);
    } catch (error) {
      console.error('Get user orders failed:', error);
      throw error;
    }
  }

  // Lấy chi tiết một đơn hàng
  async getOrder(orderId) {
    try {
      return await ApiService.request(`/api/v1/orders/${orderId}/`);
    } catch (error) {
      console.error('Get order failed:', error);
      throw error;
    }
  }

  // Hủy đơn hàng
  async cancelOrder(orderId, reason = '') {
    try {
      const response = await ApiService.request(`/api/v1/orders/${orderId}/cancel/`, {
        method: 'PATCH',
        body: JSON.stringify({ reason })
      });
      
      return response;
    } catch (error) {
      console.error('Cancel order failed:', error);
      throw error;
    }
  }

  // Lấy trạng thái đơn hàng
  getOrderStatus(status) {
    const statusMap = {
      'pending': { text: 'Chờ xử lý', class: 'status-pending', color: '#f59e0b' },
      'confirmed': { text: 'Đã xác nhận', class: 'status-confirmed', color: '#3b82f6' },
      'processing': { text: 'Đang xử lý', class: 'status-processing', color: '#8b5cf6' },
      'shipped': { text: 'Đã giao hàng', class: 'status-shipped', color: '#06b6d4' },
      'delivered': { text: 'Đã nhận hàng', class: 'status-delivered', color: '#10b981' },
      'cancelled': { text: 'Đã hủy', class: 'status-cancelled', color: '#ef4444' },
      'refunded': { text: 'Đã hoàn tiền', class: 'status-refunded', color: '#6b7280' }
    };
    
    return statusMap[status] || { text: status, class: 'status-unknown', color: '#6b7280' };
  }

  // Tính tổng giá trị đơn hàng
  calculateOrderTotal(order) {
    if (!order || !order.items) return 0;
    
    let subtotal = 0;
    order.items.forEach(item => {
      const price = item.book?.price || item.price || 0;
      const quantity = item.quantity || item.qty || 0;
      subtotal += price * quantity;
    });
    
    const shipping = order.shipping_fee || 0;
    const tax = order.tax_amount || 0;
    const discount = order.discount_amount || 0;
    
    return subtotal + shipping + tax - discount;
  }

  // Format địa chỉ giao hàng
  formatShippingAddress(address) {
    if (!address) return '';
    
    const parts = [];
    if (address.street) parts.push(address.street);
    if (address.ward) parts.push(address.ward);
    if (address.district) parts.push(address.district);
    if (address.city) parts.push(address.city);
    if (address.province) parts.push(address.province);
    
    return parts.join(', ');
  }

  // Kiểm tra xem đơn hàng có thể hủy không
  canCancelOrder(order) {
    const cancellableStatuses = ['pending', 'confirmed'];
    return cancellableStatuses.includes(order.status);
  }

  // Kiểm tra xem đơn hàng có thể đánh giá không
  canReviewOrder(order) {
    return order.status === 'delivered';
  }

  // Lấy thời gian dự kiến giao hàng
  getEstimatedDelivery(order) {
    if (!order.created_at) return null;
    
    const orderDate = new Date(order.created_at);
    const estimatedDate = new Date(orderDate);
    estimatedDate.setDate(orderDate.getDate() + 7); // Dự kiến 7 ngày
    
    return estimatedDate;
  }

  // Format ngày tháng
  formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

export default new OrderService();
