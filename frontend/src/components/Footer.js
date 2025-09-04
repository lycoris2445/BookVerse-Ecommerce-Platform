import React from 'react';
import { FaFacebook, FaTwitter, FaInstagram, FaPhone, FaMapMarkerAlt, FaEnvelope, FaShieldAlt, FaTruck, FaUndoAlt } from 'react-icons/fa';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-section">
          <div className="brand-left">
            <div className="brand-name">BookVerse</div>
            <div className="slogan">Đọc sách là sống</div>
          </div>
          <p style={{ marginTop: '1rem', lineHeight: '1.5' }}>
            BookVerse là nơi bạn tìm thấy những cuốn sách hay nhất để nuôi dưỡng tâm hồn và trí tuệ. Chúng tôi cam kết mang đến trải nghiệm mua sắm tiện lợi và dịch vụ tốt nhất.
          </p>
        </div>
        <div className="footer-section">
          <h4>Chính sách & Hỗ trợ</h4>
          <ul style={{ color: '#9ca3af' }}>
            <li><a href="#">Điều khoản sử dụng</a></li>
            <li><a href="#">Chính sách bảo mật</a></li>
            <li><a href="#">Chính sách đổi trả</a></li>
            <li><a href="#">Câu hỏi thường gặp</a></li>
          </ul>
        </div>
        <div className="footer-section">
          <h4>Liên hệ</h4>
          <ul>
            <li className="icon-item"><FaMapMarkerAlt /> 48 Lê Bôi, P7, Q8, TP.HCM</li>
            <li className="icon-item"><FaPhone /> 0123 456 789</li>
            <li className="icon-item"><FaEnvelope /> support@bookverse.vn</li>
          </ul>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <a href="#" style={{ color: '#9ca3af' }}><FaFacebook size={24} /></a>
            <a href="#" style={{ color: '#9ca3af' }}><FaTwitter size={24} /></a>
            <a href="#" style={{ color: '#9ca3af' }}><FaInstagram size={24} /></a>
          </div>
        </div>
        <div className="footer-section">
          <h4>Cam kết</h4>
          <div className="icon-list">
            <div className="icon-item">
              <FaShieldAlt size={24} /> <span>Tư vấn hỗ trợ 24/7</span>
            </div>
            <div className="icon-item">
              <FaUndoAlt size={24} /> <span>7 ngày đổi trả miễn phí</span>
            </div>
            <div className="icon-item">
              <FaTruck size={24} /> <span>Miễn phí giao hàng</span>
            </div>
          </div>
        </div>
      </div>
      <div className="footer-info">
        © {new Date().getFullYear()} BookVerse.
      </div>
    </footer>
  );
}