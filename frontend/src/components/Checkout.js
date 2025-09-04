import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FaCreditCard, FaPaypal, FaMoneyBillWave, FaArrowLeft } from 'react-icons/fa';
import Payment from './Payment';

export default function Checkout({ total, onClear }) {
  const [form, setForm] = useState({ name: '', address: '' });
  const [paymentMethod, setPaymentMethod] = useState('');
  const [showPayment, setShowPayment] = useState(false);
  const [orderId, setOrderId] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!paymentMethod) {
      toast.error('Vui lòng chọn phương thức thanh toán.');
      return;
    }

    if (paymentMethod === 'paypal') {
      // Generate mock order ID for demo
      const mockOrderId = Date.now();
      setOrderId(mockOrderId);
      setShowPayment(true);
    } else if (paymentMethod === 'cod') {
      toast.success('Đơn hàng đã được xác nhận! Thanh toán khi nhận hàng.');
      onClear();
      navigate('/');
    } else {
      toast.success('Thanh toán thành công!');
      onClear();
      navigate('/');
    }
  };

  const handlePaymentSuccess = (paymentData) => {
    toast.success('Thanh toán PayPal thành công!');
    console.log('Payment successful:', paymentData);
    onClear();
    navigate('/');
  };

  const handlePaymentCancel = () => {
    setShowPayment(false);
    toast.info('Thanh toán đã bị hủy');
  };

  const handlePaymentChange = (e) => {
    setPaymentMethod(e.target.value);
  };

  // Show payment component if PayPal is selected and form submitted
  if (showPayment && paymentMethod === 'paypal') {
    return (
      <div className="payment-wrapper">
        <Payment
          orderId={orderId}
          totalAmount={total}
          onPaymentSuccess={handlePaymentSuccess}
          onPaymentCancel={handlePaymentCancel}
        />
      </div>
    );
  }

  return (
    <section className="auth-section">
      <div className="container">
        <h1>Thanh toán</h1>
        <form className="checkout-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Họ tên</label>
            <input className="input" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
          </div>
          <div className="form-group">
            <label>Địa chỉ giao hàng</label>
            <input className="input" value={form.address} onChange={e => setForm({...form, address: e.target.value})} required />
          </div>
          
          <div className="form-group">
            <label>Phương thức thanh toán</label>
            <div className="payment-options">
              <label className={`payment-card ${paymentMethod === 'card' ? 'active' : ''}`}>
                <input 
                  type="radio" 
                  name="payment" 
                  value="card" 
                  checked={paymentMethod === 'card'} 
                  onChange={handlePaymentChange} 
                />
                <FaCreditCard /> Thẻ tín dụng
              </label>
              <label className={`payment-card ${paymentMethod === 'cod' ? 'active' : ''}`}>
                <input 
                  type="radio" 
                  name="payment" 
                  value="cod" 
                  checked={paymentMethod === 'cod'} 
                  onChange={handlePaymentChange} 
                />
                <FaMoneyBillWave /> Thanh toán khi nhận hàng (COD)
              </label>
              
              <label className={`payment-card ${paymentMethod === 'paypal' ? 'active' : ''}`}>
                <input 
                  type="radio" 
                  name="payment" 
                  value="paypal" 
                  checked={paymentMethod === 'paypal'} 
                  onChange={handlePaymentChange} 
                />
                <FaPaypal /> PayPal
              </label>
            </div>
          </div>

          <div className="total-amount">Tổng cộng: {total.toLocaleString('vi-VN')}₫</div>
          <div className="form-actions">
            <button className="btn btn-primary" type="submit">Xác nhận thanh toán</button>
            <Link 
              to="/cart" 
              className="btn btn-secondary" 
              style={{ textDecoration: 'none', textAlign: 'center', width: '100%' }}
            >
              <FaArrowLeft /> Quay lại giỏ hàng
            </Link>
          </div>
        </form>
      </div>
    </section>
  );
}