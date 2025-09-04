import ApiService from './api';

class PaymentService {
  // PayPal Integration Methods
  async createPayPalOrder(orderId) {
    try {
      const response = await ApiService.request('/payments/paypal/create-order/', {
        method: 'POST',
        body: JSON.stringify({ order_id: orderId })
      });
      
      return response;
    } catch (error) {
      console.error('Create PayPal order failed:', error);
      throw error;
    }
  }

  async capturePayPalPayment(paypalOrderId) {
    try {
      const response = await ApiService.request('/payments/paypal/capture/', {
        method: 'POST',
        body: JSON.stringify({ paypal_order_id: paypalOrderId })
      });
      
      return response;
    } catch (error) {
      console.error('Capture PayPal payment failed:', error);
      throw error;
    }
  }

  // Legacy Payment Methods
  // Khởi tạo thanh toán
  async chargePayment(paymentData) {
    try {
      const response = await ApiService.request('/payments/charge/', {
        method: 'POST',
        body: JSON.stringify(paymentData)
      });
      
      return response;
    } catch (error) {
      console.error('Charge payment failed:', error);
      throw error;
    }
  }

  // Lấy trạng thái thanh toán
  async getPaymentStatus(paymentId) {
    try {
      return await ApiService.request(`/payments/${paymentId}/status/`);
    } catch (error) {
      console.error('Get payment status failed:', error);
      throw error;
    }
  }

  // Lấy thông tin thanh toán của đơn hàng
  async getOrderPayment(orderId) {
    try {
      return await ApiService.request(`/payments/order/${orderId}/`);
    } catch (error) {
      console.error('Get order payment failed:', error);
      throw error;
    }
  }

  // Lấy thông tin sandbox (môi trường test)
  async getSandboxInfo() {
    try {
      return await ApiService.request('/payments/sandbox/info/', { auth: false });
    } catch (error) {
      console.error('Get sandbox info failed:', error);
      // Return default sandbox info
      return {
        environment: 'sandbox',
        test_cards: {
          '4111111111111111': { type: 'visa', behavior: 'success' },
          '4000000000000002': { type: 'visa', behavior: 'decline' },
          '5555555555554444': { type: 'mastercard', behavior: 'success' }
        },
        description: 'Môi trường test thanh toán'
      };
    }
  }

  // Simulate webhook (môi trường test)
  async simulateWebhook(paymentId, status = 'success') {
    try {
      const response = await ApiService.request(`/payments/sandbox/webhook/${paymentId}/`, {
        method: 'POST',
        body: JSON.stringify({ status })
      });
      
      return response;
    } catch (error) {
      console.error('Simulate webhook failed:', error);
      throw error;
    }
  }

  // Get test card information
  getTestCards() {
    return [
      {
        number: '4111111111111111',
        type: 'visa',
        behavior: 'success',
        description: 'Visa - Always succeeds',
        cvv: '123',
        expiry: '12/25'
      },
      {
        number: '5555555555554444',
        type: 'mastercard',
        behavior: 'success',
        description: 'Mastercard - Always succeeds',
        cvv: '123',
        expiry: '12/25'
      },
      {
        number: '4000000000000002',
        type: 'visa',
        behavior: 'decline',
        description: 'Visa - Generic decline',
        cvv: '123',
        expiry: '12/25'
      },
      {
        number: '4000000000000069',
        type: 'visa',
        behavior: 'decline_expired',
        description: 'Visa - Expired card',
        cvv: '123',
        expiry: '12/20'
      }
    ];
  }

  // Test payment with sandbox
  async testPayment(cardData, amount, orderId) {
    try {
      const testCards = this.getTestCards();
      const testCard = testCards.find(card => card.number === cardData.cardNumber.replace(/\s/g, ''));
      
      if (testCard) {
        // Simulate different behaviors based on test card
        await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate processing time
        
        if (testCard.behavior === 'success') {
          return {
            status: 'success',
            payment_id: `test_payment_${Date.now()}`,
            message: 'Thanh toán thành công (Test)',
            amount: amount,
            card_type: testCard.type
          };
        } else {
          throw new Error(`Thanh toán thất bại: ${testCard.description}`);
        }
      }
      
      // For real cards in test mode, process normally
      return await this.processOrderPayment(orderId, 'credit_card', {
        card_number: cardData.cardNumber,
        card_holder: cardData.cardholderName,
        expiry_date: cardData.expiryDate,
        cvv: cardData.cvv
      });
      
    } catch (error) {
      console.error('Test payment failed:', error);
      throw error;
    }
  }

  // Xử lý thanh toán cho đơn hàng
  async processOrderPayment(orderId, paymentMethod, paymentDetails = {}) {
    try {
      const paymentData = {
        order_id: orderId,
        payment_method: paymentMethod,
        ...paymentDetails
      };
      
      return await this.chargePayment(paymentData);
    } catch (error) {
      console.error('Process order payment failed:', error);
      throw error;
    }
  }

  // Lấy danh sách phương thức thanh toán
  getPaymentMethods() {
    return [
      {
        id: 'credit_card',
        name: 'Thẻ tín dụng',
        icon: '💳',
        description: 'Visa, MasterCard, JCB',
        enabled: true
      },
      {
        id: 'debit_card',
        name: 'Thẻ ghi nợ',
        icon: '💳',
        description: 'Thẻ ATM nội địa',
        enabled: true
      },
      {
        id: 'momo',
        name: 'Ví MoMo',
        icon: '📱',
        description: 'Thanh toán qua ví điện tử MoMo',
        enabled: true
      },
      {
        id: 'zalopay',
        name: 'ZaloPay',
        icon: '📱',
        description: 'Thanh toán qua ví điện tử ZaloPay',
        enabled: true
      },
      {
        id: 'banking',
        name: 'Chuyển khoản ngân hàng',
        icon: '🏦',
        description: 'Internet Banking',
        enabled: true
      },
      {
        id: 'cod',
        name: 'Thanh toán khi nhận hàng',
        icon: '📦',
        description: 'Trả tiền mặt khi nhận hàng',
        enabled: true
      }
    ];
  }

  // Lấy trạng thái thanh toán với định dạng hiển thị
  getPaymentStatus(status) {
    const statusMap = {
      'pending': { text: 'Chờ thanh toán', class: 'status-pending', color: '#f59e0b' },
      'processing': { text: 'Đang xử lý', class: 'status-processing', color: '#3b82f6' },
      'success': { text: 'Thanh toán thành công', class: 'status-success', color: '#10b981' },
      'failed': { text: 'Thanh toán thất bại', class: 'status-failed', color: '#ef4444' },
      'cancelled': { text: 'Đã hủy', class: 'status-cancelled', color: '#6b7280' },
      'refunded': { text: 'Đã hoàn tiền', class: 'status-refunded', color: '#8b5cf6' }
    };
    
    return statusMap[status] || { text: status, class: 'status-unknown', color: '#6b7280' };
  }

  // Validate thông tin thẻ tín dụng
  validateCreditCard(cardData) {
    const errors = {};
    
    // Validate card number
    if (!cardData.cardNumber) {
      errors.cardNumber = 'Số thẻ không được để trống';
    } else if (!/^\d{13,19}$/.test(cardData.cardNumber.replace(/\s/g, ''))) {
      errors.cardNumber = 'Số thẻ không hợp lệ';
    }
    
    // Validate expiry date
    if (!cardData.expiryDate) {
      errors.expiryDate = 'Ngày hết hạn không được để trống';
    } else if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(cardData.expiryDate)) {
      errors.expiryDate = 'Ngày hết hạn không đúng định dạng (MM/YY)';
    } else {
      const [month, year] = cardData.expiryDate.split('/');
      const currentDate = new Date();
      const expiryDate = new Date(`20${year}`, month - 1);
      
      if (expiryDate < currentDate) {
        errors.expiryDate = 'Thẻ đã hết hạn';
      }
    }
    
    // Validate CVV
    if (!cardData.cvv) {
      errors.cvv = 'Mã CVV không được để trống';
    } else if (!/^\d{3,4}$/.test(cardData.cvv)) {
      errors.cvv = 'Mã CVV không hợp lệ';
    }
    
    // Validate cardholder name
    if (!cardData.cardholderName) {
      errors.cardholderName = 'Tên chủ thẻ không được để trống';
    } else if (cardData.cardholderName.length < 2) {
      errors.cardholderName = 'Tên chủ thẻ quá ngắn';
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  }

  // Format số thẻ tín dụng
  formatCardNumber(cardNumber) {
    return cardNumber.replace(/\s/g, '').replace(/(.{4})/g, '$1 ').trim();
  }

  // Detect loại thẻ tín dụng
  detectCardType(cardNumber) {
    const number = cardNumber.replace(/\s/g, '');
    
    if (/^4/.test(number)) return 'visa';
    if (/^5[1-5]/.test(number)) return 'mastercard';
    if (/^3[47]/.test(number)) return 'amex';
    if (/^35/.test(number)) return 'jcb';
    
    return 'unknown';
  }

  // Tính phí thanh toán
  calculatePaymentFee(amount, paymentMethod) {
    const feeRates = {
      'credit_card': 0.029, // 2.9%
      'debit_card': 0.015,  // 1.5%
      'momo': 0.02,         // 2%
      'zalopay': 0.02,      // 2%
      'banking': 0.01,      // 1%
      'cod': 0             // 0%
    };
    
    const rate = feeRates[paymentMethod] || 0;
    return Math.round(amount * rate);
  }
}

export default new PaymentService();
