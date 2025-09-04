from django.db import models


class Payment(models.Model):
    """Enhanced payment model with PayPal integration"""
    PaymentID = models.AutoField(primary_key=True, db_column='PaymentID')
    OrderID = models.IntegerField(null=True, blank=True, db_column='OrderID')
    Amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='Amount')
    PaymentMethod = models.CharField(max_length=50, null=True, blank=True, db_column='Method')  # Maps to 'Method' column
    Status = models.CharField(max_length=20, default='pending', db_column='Status')
    TransactionID = models.CharField(max_length=255, null=True, blank=True, db_column='TransactionID')
    
    # PayPal specific fields
    PaypalOrderID = models.CharField(max_length=255, null=True, blank=True, db_column='PaypalOrderID')
    PaypalPayerID = models.CharField(max_length=255, null=True, blank=True, db_column='PaypalPayerID')
    PaypalPaymentID = models.CharField(max_length=255, null=True, blank=True, db_column='PaypalPaymentID')
    
    # Legacy sandbox field
    SandboxPaymentID = models.CharField(max_length=255, null=True, blank=True, db_column='SandboxPaymentID')
    PaymentDate = models.DateTimeField(null=True, blank=True, db_column='PaymentDate')
    
    class Meta:
        managed = False  # Don't create table, assume exists
        db_table = 'payment'
