from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('test/', views.test_connection, name='test-connection'),
    path('popular/', views.PopularBooksView.as_view(), name='popular-books'),
    path('user/<int:user_id>/', views.UserRecommendationsView.as_view(), name='user-recommendations'),
    path('content/', views.content_based_recommendations, name='content-based-recommendations'),
]
