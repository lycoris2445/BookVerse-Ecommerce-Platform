#  BookVerse - E-commerce Platform

##  Tổng quan
BookVerse là một nền tảng thương mại điện tử hiện đại chuyên bán sách trực tuyến với hệ thống gợi ý thông minh và tích hợp thanh toán PayPal.

##  Tính năng chính

###  E-commerce Core
- **Catalog Management**: Quản lý sản phẩm, danh mục sách
- **Shopping Cart**: Giỏ hàng với tính năng thêm/xóa/cập nhật
- **Order Management**: Quản lý đơn hàng và trạng thái giao dịch
- **User Authentication**: Đăng nhập/đăng ký với JWT tokens
- **Inventory Tracking**: Theo dõi tồn kho và số lượng sản phẩm

###  Payment Integration
- **PayPal Sandbox**: Tích hợp thanh toán PayPal đầy đủ
- **Order Processing**: Xử lý đơn hàng tự động
- **Webhook Support**: Xử lý callback từ PayPal
- **Transaction History**: Lịch sử giao dịch chi tiết

###  AI Recommendations
- **Content-based Filtering**: Gợi ý dựa trên nội dung sách
- **User Behavior Tracking**: Theo dõi hoạt động người dùng
- **Similar Products**: Gợi ý sản phẩm tương tự
- **Popular Items**: Hiển thị sách phổ biến

###  Analytics & Tracking
- **User Activity**: Theo dõi lượt xem, thêm vào giỏ hàng
- **Purchase Patterns**: Phân tích mẫu mua hàng
- **Recommendation Performance**: Đánh giá hiệu quả gợi ý

##  Kiến trúc hệ thống

### Backend (Django REST Framework)
`
backend/
 apps/
    catalog/         # Quản lý sản phẩm
    cart/           # Giỏ hàng
    orders/         # Đơn hàng
    payments/       # Thanh toán PayPal
    recommendations/ # Hệ thống gợi ý
    users/          # Quản lý người dùng
    activities/     # Theo dõi hoạt động
 config/            # Cấu hình Django
 requirements.txt   # Dependencies
`

### Frontend (React.js)
`
frontend/
 src/
    components/    # React components
    services/     # API services
    pages/        # App pages
    utils/        # Utilities
 package.json      # Dependencies
`

##  Cài đặt và chạy

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm/yarn

### Backend Setup
\\\ash
cd backend
pip install -r requirements.txt

# Tạo file .env
cp .env.example .env
# Cập nhật thông tin database và PayPal credentials

# Migrate database
python manage.py migrate

# Chạy server
python manage.py runserver
\\\

### Frontend Setup
\\\ash
cd frontend
npm install

# Chạy development server
npm start
\\\

##  Cấu hình Environment

### Backend (.env)
\\\
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/bookverse

# PayPal Sandbox
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
\\\

### Frontend (.env)
\\\
REACT_APP_API_URL=http://localhost:8000
REACT_APP_PAYPAL_CLIENT_ID=your_client_id
\\\

##  Production Deployment

### Render.com Deployment
1. **Backend**: Deploy Django app với environment variables
2. **Frontend**: Deploy React app với build tự động
3. **Database**: PostgreSQL database
4. **Domain**: Cấu hình custom domain

### Environment Variables (Production)
\\\
DEBUG=False
ALLOWED_HOSTS=ecomtech.onrender.com
DATABASE_URL=postgresql://...
PAYPAL_CLIENT_ID=production_client_id
PAYPAL_CLIENT_SECRET=production_client_secret
PAYPAL_BASE_URL=https://api-m.paypal.com
\\\

##  API Endpoints

### Authentication
- \POST /api/v1/auth/login/\ - Đăng nhập
- \POST /api/v1/auth/register/\ - Đăng ký
- \POST /api/v1/auth/logout/\ - Đăng xuất

### Catalog
- \GET /api/v1/catalog/products/\ - Danh sách sản phẩm
- \GET /api/v1/catalog/products/{id}/\ - Chi tiết sản phẩm
- \GET /api/v1/catalog/categories/\ - Danh mục

### Cart
- \GET /api/v1/cart/\ - Xem giỏ hàng
- \POST /api/v1/cart/add/\ - Thêm vào giỏ
- \PUT /api/v1/cart/update/{id}/\ - Cập nhật số lượng
- \DELETE /api/v1/cart/remove/{id}/\ - Xóa khỏi giỏ

### Orders
- \POST /api/v1/orders/create/\ - Tạo đơn hàng
- \GET /api/v1/orders/\ - Lịch sử đơn hàng
- \GET /api/v1/orders/{id}/\ - Chi tiết đơn hàng

### Payments
- \POST /api/v1/payments/paypal/create-order/\ - Tạo PayPal order
- \POST /api/v1/payments/paypal/capture-payment/\ - Capture payment
- \POST /api/v1/payments/paypal/webhook/\ - PayPal webhook

### Recommendations
- \GET /api/v1/recommendations/\ - Gợi ý cho user
- \GET /api/v1/recommendations/similar/{product_id}/\ - Sản phẩm tương tự
- \GET /api/v1/recommendations/popular/\ - Sản phẩm phổ biến

##  Testing

### Backend Tests
\\\ash
cd backend
python manage.py test
\\\

### Frontend Tests
\\\ash
cd frontend
npm test
\\\

##  Dependencies

### Backend Key Dependencies
- Django 4.2+
- Django REST Framework
- psycopg2-binary (PostgreSQL)
- requests (HTTP calls)
- django-cors-headers
- python-dotenv

### Frontend Key Dependencies
- React 18
- Axios (HTTP client)
- React Router DOM
- React Toastify (Notifications)
- PayPal JavaScript SDK

##  Security Features
- JWT Authentication
- CORS Configuration
- Environment Variables Protection
- Input Validation & Sanitization
- PayPal Webhook Verification

##  Development Roadmap
- [ ] Social Authentication (Google, Facebook)
- [ ] Advanced Search & Filters
- [ ] Wishlist Functionality
- [ ] Review & Rating System
- [ ] Email Notifications
- [ ] Mobile App (React Native)
- [ ] Admin Dashboard
- [ ] Analytics Dashboard

##  Contributing
1. Fork the repository
2. Create feature branch (\git checkout -b feature/amazing-feature\)
3. Commit changes (\git commit -m 'Add amazing feature'\)
4. Push to branch (\git push origin feature/amazing-feature\)
5. Open Pull Request

##  License
MIT License - see LICENSE file for details

##  Contact
- **Developer**: BookVerse Team
- **Email**: contact@bookverse.com
- **Website**: https://ecomtech.onrender.com

---
 **Star this repo if you find it helpful!**
