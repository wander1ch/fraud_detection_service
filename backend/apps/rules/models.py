from django.db import models
import json
from django.core.serializers.json import DjangoJSONEncoder

class RuleType(models.TextChoices):
    THRESHOLD = 'threshold', 'Threshold Rule'
    COMPOSITE = 'composite', 'Composite Rule'
    ML_BASED = 'ml_based', 'ML Based Rule'

class Rule(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20, choices=RuleType.choices)
    condition = models.JSONField(help_text="JSON condition for the rule")
    threshold = models.FloatField(null=True, blank=True, help_text="Threshold value for threshold rules")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.type})"

class Alert(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='alerts')
    transaction_id = models.CharField(max_length=100, db_index=True)
    reason = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    transaction_data = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"Alert {self.id} for {self.transaction_id}"

class RuleMetrics(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='metrics')
    evaluations_count = models.PositiveIntegerField(default=0)
    triggers_count = models.PositiveIntegerField(default=0)
    avg_processing_time = models.FloatField(default=0.0)
    last_evaluated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rule_metrics'
        verbose_name_plural = 'Rule Metrics'
    
    def __str__(self):
        return f"Metrics for {self.rule.name}"