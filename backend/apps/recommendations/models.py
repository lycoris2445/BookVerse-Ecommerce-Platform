from django.db import models
from django.contrib.auth.models import User

# Chỉ sử dụng các bảng có sẵn trong database, không tạo bảng mới
# Recommendation engine sẽ dựa trên:
# - useractivity: theo dõi hành vi người dùng
# - book: thông tin sách
# - customer: thông tin khách hàng
# - orders, orderdetail: lịch sử mua hàng
