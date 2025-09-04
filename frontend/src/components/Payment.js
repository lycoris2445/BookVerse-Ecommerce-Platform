import React, { useState, useEffect } from 'react';
import { paymentService } from '../services';
import toast from 'react-hot-toast';

const Payment = ({ orderId, totalAmount, onPaymentSuccess, onPaymentCancel }) => {
  const [loading, setLoading] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState('ready'); // 'ready', 'processing', 'success', 'failed'
  const [paypalOrderId, setPaypalOrderId] = useState(null);

  // Load PayPal SDK script
  useEffect(() => {
    const loadPayPalScript = () => {
      if (window.paypal) return Promise.resolve();

      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = `https://www.paypal.com/sdk/js?client-id=AQ3aier7n8biTEQWSB-457vXd23i_bgPftxf15QgKKzuco2VpSoG1yLdfCE4NKm9ppb4j_T7NoKxwQJL&currency=USD`;
        script.async = true;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error('PayPal SDK failed to load'));
        document.head.appendChild(script);
      });
    };

    loadPayPalScript()
      .then(() => {
        console.log('PayPal SDK loaded successfully');
        renderPayPalButton();
      })
      .catch(error => {
        console.error('Failed to load PayPal SDK:', error);
        toast.error('Failed to load PayPal payment system');
      });
  }, [orderId]);

  const renderPayPalButton = () => {
    if (!window.paypal || !orderId) return;

    window.paypal.Buttons({
      createOrder: async () => {
        try {
          setLoading(true);
          setPaymentStatus('processing');
          
          const response = await paymentService.createPayPalOrder(orderId);
          
          if (response.success) {
            setPaypalOrderId(response.paypal_order_id);
            toast.success('PayPal order created successfully');
            return response.paypal_order_id;
          } else {
            throw new Error(response.error || 'Failed to create PayPal order');
          }
        } catch (error) {
          console.error('Create PayPal order error:', error);
          toast.error('Failed to create PayPal order');
          setPaymentStatus('failed');
          throw error;
        } finally {
          setLoading(false);
        }
      },

      onApprove: async (data) => {
        try {
          setLoading(true);
          
          const response = await paymentService.capturePayPalPayment(data.orderID);
          
          if (response.success) {
            setPaymentStatus('success');
            toast.success('Payment completed successfully!');
            
            if (onPaymentSuccess) {
              onPaymentSuccess({
                paymentId: response.payment_id,
                transactionId: response.transaction_id,
                paypalOrderId: data.orderID,
                status: 'completed'
              });
            }
          } else {
            throw new Error(response.error || 'Payment capture failed');
          }
        } catch (error) {
          console.error('PayPal capture error:', error);
          toast.error('Payment failed. Please try again.');
          setPaymentStatus('failed');
        } finally {
          setLoading(false);
        }
      },

      onCancel: () => {
        setPaymentStatus('ready');
        toast.info('Payment cancelled');
        
        if (onPaymentCancel) {
          onPaymentCancel();
        }
      },

      onError: (err) => {
        console.error('PayPal error:', err);
        setPaymentStatus('failed');
        toast.error('Payment error occurred');
      }
    }).render('#paypal-button-container');
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(amount);
  };

  return (
    <div className="payment-container">
      <div className="payment-header">
        <h3>Complete Your Payment</h3>
        <div className="order-summary">
          <p><strong>Order #{orderId}</strong></p>
          <p className="total-amount">Total: {formatCurrency(totalAmount)}</p>
        </div>
      </div>

      <div className="payment-methods">
        <div className="payment-method paypal-method">
          <h4>Pay with PayPal</h4>
          
          {paymentStatus === 'processing' && (
            <div className="payment-loading">
              <div className="spinner"></div>
              <p>Processing payment...</p>
            </div>
          )}

          {paymentStatus === 'success' && (
            <div className="payment-success">
              <div className="success-icon">✓</div>
              <p>Payment completed successfully!</p>
            </div>
          )}

          {paymentStatus === 'failed' && (
            <div className="payment-failed">
              <div className="error-icon">✗</div>
              <p>Payment failed. Please try again.</p>
              <button 
                onClick={() => {
                  setPaymentStatus('ready');
                  renderPayPalButton();
                }}
                className="retry-button"
              >
                Retry Payment
              </button>
            </div>
          )}

          {(paymentStatus === 'ready') && (
            <div id="paypal-button-container" className="paypal-buttons"></div>
          )}
        </div>
      </div>

      <div className="payment-info">
        <p className="info-text">
          🔒 Your payment is secured by PayPal's encryption technology
        </p>
        <p className="sandbox-notice">
          ⚠️ This is a sandbox environment for testing purposes
        </p>
      </div>

      <style jsx>{`
        .payment-container {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .payment-header {
          text-align: center;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 1px solid #eee;
        }

        .payment-header h3 {
          color: #333;
          margin-bottom: 15px;
        }

        .order-summary {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 6px;
          margin-top: 15px;
        }

        .total-amount {
          font-size: 1.2em;
          font-weight: bold;
          color: #007bff;
          margin-top: 5px;
        }

        .payment-methods {
          margin-bottom: 30px;
        }

        .payment-method {
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 15px;
        }

        .paypal-method {
          border-color: #0070ba;
        }

        .payment-method h4 {
          margin-top: 0;
          margin-bottom: 15px;
          color: #333;
        }

        .payment-loading {
          text-align: center;
          padding: 20px;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #f3f3f3;
          border-top: 4px solid #007bff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 15px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .payment-success {
          text-align: center;
          padding: 20px;
          color: #28a745;
        }

        .success-icon {
          font-size: 48px;
          margin-bottom: 10px;
        }

        .payment-failed {
          text-align: center;
          padding: 20px;
          color: #dc3545;
        }

        .error-icon {
          font-size: 48px;
          margin-bottom: 10px;
        }

        .retry-button {
          background: #dc3545;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          margin-top: 15px;
        }

        .retry-button:hover {
          background: #c82333;
        }

        .paypal-buttons {
          min-height: 50px;
        }

        .payment-info {
          text-align: center;
          font-size: 0.9em;
          color: #666;
        }

        .info-text {
          margin-bottom: 10px;
        }

        .sandbox-notice {
          background: #fff3cd;
          color: #856404;
          padding: 8px 12px;
          border-radius: 4px;
          border: 1px solid #ffeaa7;
          margin-top: 15px;
        }

        ${loading ? `
          .paypal-buttons {
            pointer-events: none;
            opacity: 0.6;
          }
        ` : ''}
      `}</style>
    </div>
  );
};

export default Payment;
