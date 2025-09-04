import React, { useState, useEffect } from "react";
import ProductModal from "./ProductModal";
import { catalogService } from "../services";
import ProductImage from './ProductImage';

export default function ProductList({ query = "", category = "all", onAddToCart, onCategoryChange }) {
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totalPages, setTotalPages] = useState(0);
  const itemsPerPage = 12;

  // Fetch books from API
  useEffect(() => {
    const fetchBooks = async () => {
      try {
        setLoading(true);
        const params = {
          page,
          limit: itemsPerPage
        };

        if (category && category !== 'all') {
          params.category = category;
        }

        if (query && query.trim()) {
          params.search = query.trim();
        }

        const response = await catalogService.getBooks(params);
        
        if (response.success) {
          setBooks(response.data || []);
          setTotalPages(Math.ceil((response.total || 0) / itemsPerPage));
        }
      } catch (error) {
        console.error('Error fetching books:', error);
        setBooks([]);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [query, category, page]);

  // Fetch categories
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await catalogService.getCategories();
        if (response.success) {
          setCategories(response.data || []);
        }
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return <div className="loading">Đang tải sách từ database...</div>;
  }

  return (
    <section>
      <h2 className="section-title">Sách nổi bật</h2>
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">Danh mục</label>
          <select 
            value={category} 
            onChange={e => onCategoryChange && onCategoryChange(e.target.value)} 
            className="input category-inline-select"
          >
            <option value="all">Tất cả</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
        </div>
      </div>

      {books.length === 0 ? (
        <div className="no-results">
          <p>Không tìm thấy sách nào {query && `cho "${query}"`}</p>
        </div>
      ) : (
        <>
          <div className="product-grid">
            {books.map((book) => (
              <div key={book.id} className="product-card" onClick={() => setSelected(book)}>
                <div className="product-image">
                  <ProductImage 
                    src={book.image_url || book.coverImage} 
                    alt={book.title}
                    width="100%"
                    height={280}
                  />
                </div>
                <div className="product-info">
                  <h3 className="product-title">{book.title}</h3>
                  <p className="product-author">Tác giả: {book.author}</p>
                  <p className="product-price">{(book.price || 0).toLocaleString('vi-VN')}₫</p>
                  {book.description && (
                    <p className="product-description">{book.description.slice(0, 100)}...</p>
                  )}
                  <div className="product-actions">
                    <button 
                      className="btn btn-primary"
                      onClick={(e) => {
                        e.stopPropagation();
                        onAddToCart(book);
                      }}
                    >
                      Thêm vào giỏ hàng
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button 
                className="btn" 
                onClick={() => setPage(p => Math.max(1, p - 1))} 
                disabled={page === 1}
              >
                Trước
              </button>
              <span>Trang {page} / {totalPages}</span>
              <button 
                className="btn" 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))} 
                disabled={page === totalPages}
              >
                Tiếp
              </button>
            </div>
          )}
        </>
      )}
      
      <ProductModal 
        product={selected} 
        onClose={() => setSelected(null)} 
        onAddToCart={onAddToCart} 
      />
    </section>
  );
}
