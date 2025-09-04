import ApiService from './api';

class AuthService {
  // Đăng ký người dùng mới
  async register(userData) {
    try {
      const response = await ApiService.request('/api/v1/users/register/', {
        method: 'POST',
        body: JSON.stringify(userData),
        auth: false
      });
      
      if (response.token) {
        ApiService.setToken(response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      
      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  // Đăng nhập
  async login(credentials) {
    try {
      const response = await ApiService.request('/api/v1/users/login/', {
        method: 'POST',
        body: JSON.stringify(credentials),
        auth: false
      });
      
      if (response.token) {
        ApiService.setToken(response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  // Đăng xuất
  async logout() {
    try {
      await ApiService.request('/api/v1/users/logout/', {
        method: 'POST'
      });
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      // Luôn clear local storage
      ApiService.setToken(null);
      localStorage.removeItem('user');
    }
  }

  // Lấy thông tin user hiện tại
  async getCurrentUser() {
    try {
      const response = await ApiService.request('/api/v1/users/me/');
      return response;
    } catch (error) {
      console.error('Get current user failed:', error);
      throw error;
    }
  }

  // Lấy thông tin user từ localStorage
  getUserFromStorage() {
    try {
      const user = localStorage.getItem('user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error parsing user from storage:', error);
      return null;
    }
  }

  // Kiểm tra xem user có đăng nhập không
  isAuthenticated() {
    return !!ApiService.token && !!this.getUserFromStorage();
  }

  // Refresh user data
  async refreshUser() {
    if (!this.isAuthenticated()) {
      return null;
    }
    
    try {
      const user = await this.getCurrentUser();
      localStorage.setItem('user', JSON.stringify(user));
      return user;
    } catch (error) {
      // Token có thể đã hết hạn, đăng xuất
      this.logout();
      return null;
    }
  }
}

export default new AuthService();
