import ApiService from './api';

class CartService {
  // Lấy giỏ hàng hiện tại
  async getCart() {
    try {
      return await ApiService.request('/orders/cart/');
    } catch (error) {
      console.error('Get cart failed:', error);
      throw error;
    }
  }

  // Thêm sản phẩm vào giỏ hàng
  async addToCart(bookId, quantity = 1) {
    try {
      const response = await ApiService.request('/orders/cart/items/', {
        method: 'POST',
        body: JSON.stringify({
          book_id: bookId,
          qty: quantity
        })
      });
      
      return response;
    } catch (error) {
      console.error('Add to cart failed:', error);
      throw error;
    }
  }

  // Cập nhật số lượng sản phẩm trong giỏ hàng
  async updateItemQuantity(bookId, quantity) {
    try {
      const response = await ApiService.request('/orders/cart/items/qty/', {
        method: 'PATCH',
        body: JSON.stringify({
          book_id: bookId,
          qty: quantity
        })
      });
      
      return response;
    } catch (error) {
      console.error('Update cart item quantity failed:', error);
      throw error;
    }
  }

  // Xóa sản phẩm khỏi giỏ hàng
  async removeFromCart(bookId) {
    try {
      const response = await ApiService.request(`/orders/cart/items/${bookId}/`, {
        method: 'DELETE'
      });
      
      return response;
    } catch (error) {
      console.error('Remove from cart failed:', error);
      throw error;
    }
  }

  // Tăng số lượng sản phẩm
  async increaseQuantity(bookId, currentQuantity = 1) {
    return await this.updateItemQuantity(bookId, currentQuantity + 1);
  }

  // Giảm số lượng sản phẩm
  async decreaseQuantity(bookId, currentQuantity = 1) {
    if (currentQuantity <= 1) {
      return await this.removeFromCart(bookId);
    }
    return await this.updateItemQuantity(bookId, currentQuantity - 1);
  }

  // Clear toàn bộ giỏ hàng (thực hiện bằng cách xóa từng item)
  async clearCart() {
    try {
      const cart = await this.getCart();
      if (cart.items && cart.items.length > 0) {
        // Xóa từng item trong giỏ hàng
        const deletePromises = cart.items.map(item => 
          this.removeFromCart(item.book_id || item.book.id)
        );
        await Promise.all(deletePromises);
      }
      return { success: true };
    } catch (error) {
      console.error('Clear cart failed:', error);
      throw error;
    }
  }

  // Tính tổng số lượng items trong giỏ hàng
  getCartItemCount(cart) {
    if (!cart || !cart.items) return 0;
    return cart.items.reduce((total, item) => total + (item.quantity || item.qty || 0), 0);
  }

  // Tính tổng giá trị giỏ hàng
  getCartTotal(cart) {
    if (!cart || !cart.items) return 0;
    return cart.items.reduce((total, item) => {
      const price = item.book?.price || item.price || 0;
      const quantity = item.quantity || item.qty || 0;
      return total + (price * quantity);
    }, 0);
  }

  // Kiểm tra xem sản phẩm có trong giỏ hàng không
  isInCart(cart, bookId) {
    if (!cart || !cart.items) return false;
    return cart.items.some(item => 
      (item.book_id || item.book?.id) === bookId
    );
  }

  // Lấy quantity của một sản phẩm trong giỏ hàng
  getItemQuantity(cart, bookId) {
    if (!cart || !cart.items) return 0;
    const item = cart.items.find(item => 
      (item.book_id || item.book?.id) === bookId
    );
    return item ? (item.quantity || item.qty || 0) : 0;
  }

  // Sync giỏ hàng từ localStorage (nếu user chưa đăng nhập)
  async syncLocalCartToServer(localCart) {
    try {
      if (!localCart || localCart.length === 0) return;
      
      // Thêm từng item từ local cart vào server cart
      for (const item of localCart) {
        await this.addToCart(item.id, item.quantity);
      }
      
      return { success: true };
    } catch (error) {
      console.error('Sync local cart failed:', error);
      throw error;
    }
  }
}

export default new CartService();
