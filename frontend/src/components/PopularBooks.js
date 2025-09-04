import React, { useState, useEffect } from 'react';
import { catalogService } from '../services';
import ProductModal from './ProductModal';
import ProductImage from './ProductImage';
import './PopularBooks.css';

const PopularBooks = ({ onAddToCart }) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedBook, setSelectedBook] = useState(null);

  const formatPrice = (price) => {
    const numPrice = Number(price);
    if (!price || isNaN(numPrice) || numPrice < 0) {
      return 'Liên hệ';
    }
    return `${numPrice.toLocaleString('vi-VN')}đ`;
  };

  const fetchPopularBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch all books then randomly select 4
      const response = await catalogService.getBooks();
      if (response && response.results && Array.isArray(response.results)) {
        // Shuffle array and take first 4
        const shuffled = [...response.results].sort(() => 0.5 - Math.random());
        setBooks(shuffled.slice(0, 4));
      } else {
        setBooks([]);
      }
    } catch (err) {
      console.error('Error fetching popular books:', err);
      setError('Không thể tải danh sách sách phổ biến');
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPopularBooks();
  }, []);

  if (loading) {
    return (
      <section className="popular-books-section">
        <div className="container">
          <h2>📈 Sách được mua nhiều</h2>
          <div className="popular-books-loading">
            <div className="loading-spinner">Đang tải...</div>
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="popular-books-section">
        <div className="container">
          <h2>📈 Sách được mua nhiều</h2>
          <div className="popular-books-error">
            <p>{error}</p>
            <button onClick={fetchPopularBooks} className="btn btn-primary">
              Thử lại
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (books.length === 0) {
    return (
      <section className="popular-books-section">
        <div className="container">
          <h2>📈 Sách được mua nhiều</h2>
          <p>Không có dữ liệu sách phổ biến.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="popular-books-section">
      <div className="container">
        <h2>📈 Sách được mua nhiều</h2>
        <div className="popular-books-grid">
          {books.map((book) => (
            <div 
              key={book.BookID || book.id} 
              className="popular-book-card"
              onClick={() => setSelectedBook(book)}
            >
              <div className="popular-book-image">
                <ProductImage
                  src={book.ImageURL || book.image_url || book.coverImage}
                  alt={book.Title || book.title}
                  width="100%"
                  height={300}
                />
                <div className="popular-book-overlay">
                  <span className="quick-view">Xem chi tiết</span>
                </div>
              </div>
              <div className="popular-book-info">
                <h3 className="popular-book-title">
                  {book.Title || book.title || 'Chưa có tiêu đề'}
                </h3>
                <p className="popular-book-author">
                  {book.AuthorName || book.author || 'Chưa rõ tác giả'}
                </p>
                <p className="popular-book-price">
                  {formatPrice(book.Price || book.price)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Product Modal */}
      {selectedBook && (
        <ProductModal
          product={{
            ...selectedBook,
            title: selectedBook.Title || selectedBook.title,
            author: selectedBook.AuthorName || selectedBook.author,
            price: selectedBook.Price || selectedBook.price,
            description: selectedBook.Description || selectedBook.description || 'Chưa có mô tả',
            coverImage: selectedBook.ImageURL || selectedBook.image_url || selectedBook.coverImage
          }}
          onClose={() => setSelectedBook(null)}
          onAddToCart={onAddToCart}
        />
      )}
    </section>
  );
};

export default PopularBooks;
