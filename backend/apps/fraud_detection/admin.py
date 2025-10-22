from django.contrib import admin
from .models import Transaction, Rule, Alert

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'timestamp', 'is_fraud', 'status']
    list_filter = ['is_fraud', 'status', 'timestamp']
    search_fields = ['user__username', 'transaction_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'rule', 'created_at', 'status']
    list_filter = ['status', 'created_at', 'rule']
    search_fields = ['transaction__id', 'rule__name']
    readonly_fields = ['created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'timestamp', 'is_fraud', 'status', 'triggered_rules']

    # ... остальные настройки

    def triggered_rules(self, obj):
        alerts = Alert.objects.filter(transaction=obj)
        return ", ".join([alert.rule.name for alert in alerts])

    triggered_rules.short_description = 'Triggered Rules'