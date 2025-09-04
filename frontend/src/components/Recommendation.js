import React, { useMemo, useRef } from "react";
import { Link } from "react-router-dom";
import { BOOKS } from "./ProductList";
import { FaChevronLeft, FaChevronRight } from "react-icons/fa";
import PropTypes from "prop-types";
import ProductImage from './ProductImage';

export default function Recommendation({ current = null, category = "all", title = "Có thể bạn sẽ thích", items = null }) {
  const carouselRef = useRef(null);

  const recItems = useMemo(() => {
    if (items) return items;
    let filtered = BOOKS.filter(b => b.id !== (current?.id || ""));
    if (current) {
      const sameCategory = filtered.filter(b => b.category === current.category);
      const others = filtered.filter(b => b.category !== current.category);
      filtered = [...sameCategory, ...others].slice(0, 8);
    } else if (category !== "all") {
      filtered = filtered.filter(b => b.category === category).slice(0, 8);
    } else {
      filtered = filtered.sort(() => Math.random() - 0.5).slice(0, 8);
    }
    return filtered;
  }, [current, category, items]);

  const scrollLeft = () => {
    if (carouselRef.current) {
      carouselRef.current.scrollBy({ left: -200, behavior: "smooth" });
    }
  };

  const scrollRight = () => {
    if (carouselRef.current) {
      carouselRef.current.scrollBy({ left: 200, behavior: "smooth" });
    }
  };

  return (
    <section className="recommendation">
      <h3 className="recommendation-title">{title}</h3>
      <div className="carousel-wrapper">
        <button className="carousel-btn carousel-prev" onClick={scrollLeft} aria-label="Previous">
          <FaChevronLeft />
        </button>
        <div className="carousel" ref={carouselRef}>
          <div className="carousel-inner">
            {recItems.map(b => (
              <Link to={`/product/${b.BookID || b.id}`} key={b.BookID || b.id} className="card rec-card">
                <ProductImage
                  src={b.coverImage || b.ImageURL || b.image_url}
                  alt={b.title || b.Title}
                  className="rec-image"
                  width={180}
                  height={220}
                  style={{ borderRadius: '8px' }}
                />
                <div className="card-body">
                  <div className="rec-title">{b.title || b.Title}</div>
                  <div className="muted rec-rating">★ {b.rating || '5.0'}</div>
                  <div className="muted rec-author">{b.author || 'Chưa có thông tin'}</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
        <button className="carousel-btn carousel-next" onClick={scrollRight} aria-label="Next">
          <FaChevronRight />
        </button>
      </div>
    </section>
  );
}

Recommendation.propTypes = {
  current: PropTypes.shape({
    id: PropTypes.string.isRequired,
    category: PropTypes.string.isRequired,
  }),
  category: PropTypes.string,
  title: PropTypes.string,
  items: PropTypes.array
};