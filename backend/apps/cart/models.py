from django.db import models


class CartItem(models.Model):
    """
    Virtual cart item model for serializer validation only
    Actual cart data is stored in Orders table with status='cart'
    """
    book_id = models.IntegerField()
    quantity = models.IntegerField(default=1)
    
    class Meta:
        # This is a virtual model for validation only
        managed = False
