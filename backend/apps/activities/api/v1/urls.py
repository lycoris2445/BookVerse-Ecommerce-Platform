from django.urls import path
from .views import create_activity, create_activity_bulk

urlpatterns = [
    path("", create_activity, name="activity-create"),
    path("bulk/", create_activity_bulk, name="activity-bulk-create"),
]
