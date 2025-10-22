from django.contrib import admin
from apps.transactions.models import Transactions as Transaction
from apps.notifications.models import Notification as Alert


from apps.fraud_detection.models import Alert  

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction', 'rule', 'created_at', 'status']
    list_filter = ['status', 'created_at', 'rule']
    readonly_fields = ['created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'value', 'created_at', 'fraud_flag']
    list_filter = ['fraud_flag', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def triggered_rules(self, obj):
        alerts = Alert.objects.filter(transaction=obj)
        return ", ".join([alert.rule.name for alert in alerts])
    triggered_rules.short_description = 'Triggered Rules'


