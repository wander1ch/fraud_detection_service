from django.contrib import admin
from .models import Rule, Alert, RuleMetrics

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'threshold', 'active', 'created_at']
    list_filter = ['type', 'active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'rule', 'severity', 'created_at']
    list_filter = ['severity', 'created_at', 'rule']
    search_fields = ['transaction_id', 'reason']
    readonly_fields = ['created_at']

@admin.register(RuleMetrics)
class RuleMetricsAdmin(admin.ModelAdmin):
    list_display = ['rule', 'evaluations_count', 'triggers_count', 'avg_processing_time', 'last_evaluated']
    readonly_fields = ['evaluations_count', 'triggers_count', 'avg_processing_time', 'last_evaluated']