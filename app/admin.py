from django.contrib import admin
from .models import Transaction, FraudRule, FraudCheckResult, SystemStats

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['correlation_id', 'amount', 'from_account', 'to_account', 'status', 'is_fraud', 'timestamp']
    list_filter = ['status', 'is_fraud', 'timestamp']
    search_fields = ['correlation_id', 'from_account', 'to_account']
    
    # Поля только для чтения
    readonly_fields = ['id', 'correlation_id', 'timestamp', 'status', 'is_fraud', 'fraud_score']
    
    # Порядок полей в форме
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'correlation_id', 'timestamp')
        }),
        ('Данные транзакции', {
            'fields': ('amount', 'from_account', 'to_account')
        }),
        ('Результат проверки', {
            'fields': ('status', 'is_fraud', 'fraud_score'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FraudRule)
class FraudRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active', 'created_at']
    list_filter = ['rule_type', 'is_active']
    search_fields = ['name', 'description']
    
    # Динамические fieldsets в зависимости от типа правила
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Основная информация', {
                'fields': ('name', 'rule_type', 'description', 'is_active')
            }),
        ]
        
        if obj and obj.rule_type == 'threshold':
            fieldsets.append(('Параметры порогового правила', {
                'fields': ('threshold_amount',),
                'classes': ('collapse',)
            }))
        elif obj and obj.rule_type == 'composite':
            fieldsets.append(('Параметры составного правила', {
                'fields': ('composite_amount', 'nighttime_start', 'nighttime_end'),
                'classes': ('collapse',)
            }))
        elif obj and obj.rule_type == 'ml':
            fieldsets.append(('Параметры ML правила', {
                'fields': ('ml_threshold',),
                'classes': ('collapse',)
            }))
            
        return fieldsets

@admin.register(FraudCheckResult)
class FraudCheckResultAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'checked_at', 'total_rules_checked', 'final_score']
    list_filter = ['checked_at']
    readonly_fields = ['checked_at', 'total_rules_checked', 'triggered_rules', 'final_score', 'details']
    
    def has_add_permission(self, request):
        return False  # Запрещаем ручное создание

@admin.register(SystemStats)
class SystemStatsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_processed', 'total_suspicious', 'total_fraud']
    readonly_fields = ['date', 'total_processed', 'total_suspicious', 'total_fraud', 'avg_processing_time']
    
    def has_add_permission(self, request):
        return False  # Запрещаем ручное создание