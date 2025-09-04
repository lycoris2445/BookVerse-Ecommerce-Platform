from django.urls import path
from .views import register, login_view, logout_view, me, UserList, UserDetail

urlpatterns = [
    path('register/', register, name='user-register'),
    path('login/', login_view, name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('me/', me, name='user-me'),
    path('', UserList.as_view(), name='user-list'),
    path('<int:pk>/', UserDetail.as_view(), name='user-detail'),
]
