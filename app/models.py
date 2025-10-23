# app/models.py
from django.db import models
import uuid

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'В обработке'),
        ('completed', 'Завершена'),
        ('suspicious', 'Подозрительная'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    from_account = models.CharField(max_length=255)
    to_account = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    correlation_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_fraud = models.BooleanField(default=False)
    fraud_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Transaction {self.correlation_id} - {self.amount}"

class FraudRule(models.Model):
    RULE_TYPES = [
        ('threshold', 'Пороговое правило'),
        ('pattern', 'Паттерн'),
        ('composite', 'Составное правило'),
        ('ml', 'ML правило'),
    ]
    
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Параметры для разных типов правил
    threshold_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Поля для составных правил
    composite_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, default=50000)
    nighttime_start = models.TimeField(null=True, blank=True, default='22:00:00')
    nighttime_end = models.TimeField(null=True, blank=True, default='06:00:00')
    
    pattern_config = models.TextField(null=True, blank=True)
    ml_threshold = models.FloatField(default=0.8)
    
    def __str__(self):
        return f"{self.name} ({self.get_rule_type_display()})"
    
class FraudCheckResult(models.Model):
    """Результат проверки транзакции на мошенничество"""
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='fraud_check')
    checked_at = models.DateTimeField(auto_now_add=True)
    total_rules_checked = models.IntegerField(default=0)
    triggered_rules = models.JSONField(default=list)  # Список сработавших правил
    final_score = models.FloatField(default=0.0)
    details = models.JSONField(default=dict)  # Детали по каждому правилу
    
    class Meta:
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"Check for {self.transaction.correlation_id}"

class SystemStats(models.Model):
    """Агрегированная статистика системы"""
    date = models.DateField(unique=True)
    total_processed = models.IntegerField(default=0)
    total_suspicious = models.IntegerField(default=0)
    total_fraud = models.IntegerField(default=0)
    avg_processing_time = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats for {self.date}"