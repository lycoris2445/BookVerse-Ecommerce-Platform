import React, { useEffect } from 'react';
import ProductImage from './ProductImage';
import { trackingService } from '../services';

const ProductModal = ({ product, onClose, onAddToCart }) => {
  if (!product) return null;

  // Track product view when modal opens
  useEffect(() => {
    if (product) {
      trackingService.trackProductView(product.BookID || product.id);
    }
  }, [product]);

  const formatPrice = (price) => {
    if (!price || price === 0) return 'Liên hệ';
    return `${parseInt(price).toLocaleString('vi-VN')}đ`;
  };

  const productData = {
    title: product.title || product.Title || 'Chưa có tiêu đề',
    author: product.author || product.AuthorName || 'Chưa rõ tác giả',
    price: product.price || product.Price || 0,
    description: product.description || product.Description || 'Chưa có mô tả sản phẩm.',
    category: product.category || product.CategoryName,
    publisher: product.publisher || product.PublisherName,
    isbn: product.isbn || product.ISBN,
    year: product.year || product.Year,
    stock: product.stock || product.Stock
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>&times;</button>
        
        <div className="modal-body">
          <div className="modal-image">
            <ProductImage
              src={product.coverImage || product.image_url || product.ImageURL}
              alt={productData.title}
              width="100%"
              height={400}
            />
          </div>
          
          <div className="modal-info">
            <h2>{productData.title}</h2>
            <p className="author">👤 <strong>Tác giả:</strong> {productData.author}</p>
            {productData.category && (
              <p className="category">📂 <strong>Thể loại:</strong> {productData.category}</p>
            )}
            {productData.publisher && (
              <p className="publisher">🏢 <strong>Nhà xuất bản:</strong> {productData.publisher}</p>
            )}
            {productData.year && (
              <p className="year">📅 <strong>Năm xuất bản:</strong> {productData.year}</p>
            )}
            {productData.isbn && (
              <p className="isbn">🔢 <strong>ISBN:</strong> {productData.isbn}</p>
            )}
            <p className="price">💰 <strong>Giá:</strong> {formatPrice(productData.price)}</p>
            {productData.stock !== undefined && (
              <p className="stock">📦 <strong>Tồn kho:</strong> {productData.stock > 0 ? `${productData.stock} cuốn` : 'Hết hàng'}</p>
            )}
            
            <div className="description-section">
              <h4>📖 Mô tả sản phẩm</h4>
              <p className="description">{productData.description}</p>
            </div>
            
            <div className="modal-actions">
              <button 
                className="btn btn-primary" 
                onClick={() => {
                  onAddToCart({
                    ...product,
                    title: productData.title,
                    author: productData.author,
                    price: productData.price
                  });
                  onClose();
                }}
                disabled={productData.stock === 0}
              >
                {productData.stock === 0 ? 'Hết hàng' : 'Thêm vào giỏ hàng'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductModal;
