// ProductDetail.js
import React, { useMemo } from "react";
import { useParams } from "react-router-dom";
import { BOOKS, formatVND } from "./ProductList";
import Recommendation from "./Recommendation";
import ProductImage from "./ProductImage";
import { FaStar, FaShoppingCart } from "react-icons/fa";

export default function ProductDetail({ onAddToCart }) {
  const { id } = useParams();
  const book = useMemo(() => BOOKS.find((b) => b.id === id), [id]);

  if (!book) return <div className="no-product">Sách không tìm thấy.</div>;

  return (
    <div className="container">
      <div className="detail-layout">
        <div className="card detail-card">
          <ProductImage
            src={book.coverImage}
            alt={book.title}
            className="detail-image"
            width="100%"
            height={500}
          />
          <div className="card-body">
            <h1>{book.title}</h1>
            <div className="muted">Tác giả: {book.author}</div>
            <div className="muted">Danh mục: {book.category}</div>
            <p className="detail-desc">{book.description}</p>
          </div>
        </div>

        <aside className="card detail-aside">
          <div className="card-body">
            <div className="aside-row">
              <div>Giá</div>
              <div className="price">{formatVND(book.price)}</div>
            </div>
            <div className="aside-actions">
              <button
                className="btn btn-primary"
                onClick={() => onAddToCart(book, 1)}
              >
                <FaShoppingCart /> Thêm vào giỏ
              </button>
              <button
                className="btn"
                onClick={() => onAddToCart(book, 1)}
              >
                Mua ngay
              </button>
            </div>
            <div className="muted aside-rating">
              <FaStar /> Đánh giá: {book.rating} / 5
            </div>
          </div>
        </aside>
      </div>

      <div style={{ marginTop: "var(--spacing-lg)" }}>
        <Recommendation current={book} title="Có thể bạn cũng thích" />
      </div>
    </div>
  );
}