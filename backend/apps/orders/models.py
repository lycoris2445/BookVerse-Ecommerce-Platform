from django.db import models


class Order(models.Model):
    OrderID = models.AutoField(primary_key=True, db_column='OrderID')
    CustomerID = models.IntegerField(null=True, blank=True, db_column='CustomerID')
    OrderDate = models.DateTimeField(null=True, blank=True, db_column='OrderDate')
    TotalAmount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='TotalAmount')
    Status = models.CharField(max_length=50, null=True, blank=True, db_column='Status')

    class Meta:
        managed = False
        db_table = 'orders'


class OrderDetail(models.Model):
    OrderDetailID = models.AutoField(primary_key=True, db_column='OrderDetailID')
    OrderID = models.IntegerField(null=True, blank=True, db_column='OrderID')
    BookID = models.IntegerField(null=True, blank=True, db_column='BookID')
    Quantity = models.IntegerField(null=True, blank=True, db_column='Quantity')
    Price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='Price')

    class Meta:
        managed = False
        db_table = 'orderdetail'
