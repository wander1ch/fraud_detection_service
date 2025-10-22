from django.db import models

from django.contrib.auth.models import User  

# Create your models here.
class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    fraud_flag = models.BooleanField(default=False)