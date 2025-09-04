from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

class UserActivity(models.Model):
    """Mapping với bảng useractivity có sẵn trong database"""
    ActivityID = models.AutoField(primary_key=True, db_column="ActivityID")
    CustomerID = models.IntegerField(db_column="CustomerID")
    BookID = models.IntegerField(db_column="BookID")
    Action = models.CharField(db_column="Action", max_length=20)
    ActivityTime = models.DateTimeField(db_column="ActivityTime")
    SessionID = models.CharField(db_column="SessionID", max_length=50, null=True, blank=True)

    class Meta:
        managed = False  # Không tạo bảng mới, chỉ mapping với bảng có sẵn
        db_table = "useractivity"

    def __str__(self):
        return f"Activity {self.ActivityID} - Customer {self.CustomerID} - {self.Action}"
