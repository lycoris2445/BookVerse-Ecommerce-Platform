from django.urls import path, include

urlpatterns = [
    path('v1/', include('apps.recommendations.api.v1.urls')),
]
