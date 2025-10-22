from django.db import models
from apps.transactions.models import Transactions
from apps.rules.models import Rule

class Alert(models.Model):
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        return f"Alert #{self.id} - {self.rule.name}"
