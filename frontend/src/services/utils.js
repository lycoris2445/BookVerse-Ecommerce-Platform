// Utility functions cho API services
export const ApiUtils = {
  // Format error messages
  formatError(error) {
    if (typeof error === 'string') return error;
    if (error.message) return error.message;
    if (error.detail) return error.detail;
    if (error.non_field_errors) return error.non_field_errors[0];
    
    // Handle field errors
    const fieldErrors = [];
    Object.keys(error).forEach(field => {
      if (Array.isArray(error[field])) {
        fieldErrors.push(`${field}: ${error[field][0]}`);
      } else if (typeof error[field] === 'string') {
        fieldErrors.push(`${field}: ${error[field]}`);
      }
    });
    
    return fieldErrors.length > 0 ? fieldErrors.join(', ') : 'Đã có lỗi xảy ra';
  },

  // Format currency
  formatCurrency(amount, currency = 'VND') {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  },

  // Format number
  formatNumber(number) {
    return new Intl.NumberFormat('vi-VN').format(number);
  },

  // Debounce function
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Validate email
  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Validate phone number (Vietnam)
  isValidPhoneNumber(phone) {
    const phoneRegex = /^(0[3|5|7|8|9])+([0-9]{8})$/;
    return phoneRegex.test(phone);
  },

  // Generate random string
  generateRandomString(length = 8) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  },

  // Storage utilities
  storage: {
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
      } catch (error) {
        console.error('Storage set error:', error);
        return false;
      }
    },

    get(key, defaultValue = null) {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch (error) {
        console.error('Storage get error:', error);
        return defaultValue;
      }
    },

    remove(key) {
      try {
        localStorage.removeItem(key);
        return true;
      } catch (error) {
        console.error('Storage remove error:', error);
        return false;
      }
    },

    clear() {
      try {
        localStorage.clear();
        return true;
      } catch (error) {
        console.error('Storage clear error:', error);
        return false;
      }
    }
  },

  // URL utilities
  buildQueryString(params) {
    const query = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
        query.append(key, params[key]);
      }
    });
    return query.toString();
  },

  parseQueryString(queryString) {
    const params = {};
    const urlParams = new URLSearchParams(queryString);
    for (const [key, value] of urlParams) {
      params[key] = value;
    }
    return params;
  },

  // Date utilities
  formatDate(date, options = {}) {
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      ...options
    };
    
    return new Date(date).toLocaleDateString('vi-VN', defaultOptions);
  },

  formatDateTime(date) {
    return new Date(date).toLocaleString('vi-VN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Array utilities
  chunk(array, size) {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
      chunks.push(array.slice(i, i + size));
    }
    return chunks;
  },

  unique(array, key = null) {
    if (!key) return [...new Set(array)];
    
    const seen = new Set();
    return array.filter(item => {
      const value = item[key];
      if (seen.has(value)) return false;
      seen.add(value);
      return true;
    });
  },

  // Object utilities
  pick(obj, keys) {
    const result = {};
    keys.forEach(key => {
      if (key in obj) result[key] = obj[key];
    });
    return result;
  },

  omit(obj, keys) {
    const result = { ...obj };
    keys.forEach(key => delete result[key]);
    return result;
  },

  // Network utilities
  async checkConnection() {
    try {
      const response = await fetch('/api/v1/healthz/', { 
        method: 'HEAD',
        cache: 'no-cache'
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  },

  // Image utilities
  getImageUrl(imagePath, baseUrl = '') {
    if (!imagePath) return '/placeholder-book.jpg';
    if (imagePath.startsWith('http')) return imagePath;
    return `${baseUrl}${imagePath}`;
  },

  // Rating utilities
  renderStars(rating, maxStars = 5) {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push('★');
    }

    if (hasHalfStar) {
      stars.push('☆');
    }

    while (stars.length < maxStars) {
      stars.push('☆');
    }

    return stars.join('');
  }
};

export default ApiUtils;
