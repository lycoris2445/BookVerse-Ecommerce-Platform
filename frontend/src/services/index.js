// Export tất cả các services
export { default as ApiService } from './api';
export { default as AuthService } from './authService';
export * as CatalogService from './catalogService'; // Changed to named exports
export { default as CartService } from './cartService';
export { default as OrderService } from './orderService';
export { default as PaymentService } from './paymentService';
export { default as RecommendationService } from './recommendationService';
export { default as TrackingService } from './tracking';

// Re-export for backward compatibility
import ApiService from './api';
import AuthService from './authService';
import * as CatalogService from './catalogService'; // Changed to import all functions
import CartService from './cartService';
import OrderService from './orderService';
import PaymentService from './paymentService';
import RecommendationService from './recommendationService';
import TrackingService from './tracking';

// Export catalog functions directly for easy access
export const catalogService = CatalogService; // Now it's an object with functions
export const authService = AuthService;
export const cartService = CartService;
export const orderService = OrderService;
export const paymentService = PaymentService;
export const recommendationService = RecommendationService;
export const trackingService = TrackingService;

export default {
  ApiService,
  AuthService,
  CatalogService,
  CartService,
  OrderService,
  PaymentService,
  RecommendationService,
  TrackingService
};
