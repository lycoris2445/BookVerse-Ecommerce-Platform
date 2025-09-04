// API Configuration và Base Service
const API_BASE_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://ecomtech.onrender.com' 
    : 'http://localhost:8000');

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get current token (realtime)
  getToken() {
    return localStorage.getItem('auth_token') || 
           localStorage.getItem('access_token') || 
           localStorage.getItem('authToken');
  }

  // Helper method to get headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      const token = this.getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    return headers;
  }

  // Helper method to handle response
  async handleResponse(response) {
    const data = await response.json().catch(() => null);
    
    if (!response.ok) {
      throw new Error(data?.message || data?.detail || `HTTP Error: ${response.status}`);
    }
    
    return data;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getHeaders(options.auth !== false),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      return await this.handleResponse(response);
    } catch (error) {
      console.error(`API Request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Update token
  setToken(token) {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export default new ApiService();
