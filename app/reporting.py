import logging
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q
from .models import Transaction, FraudCheckResult, SystemStats, FraudRule

logger = logging.getLogger(__name__)

class ReportingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def update_daily_stats(self):
        """Обновляет ежедневную статистику"""
        try:
            today = datetime.now().date()
            
            # Агрегируем данные за сегодня
            stats = Transaction.objects.filter(
                timestamp__date=today
            ).aggregate(
                total_processed=Count('id'),
                total_suspicious=Count('id', filter=Q(status='suspicious')),
                total_fraud=Count('id', filter=Q(is_fraud=True)),
                avg_processing_time=Avg('fraud_score')  # Временная метрика
            )
            
            # Создаем или обновляем запись
            SystemStats.objects.update_or_create(
                date=today,
                defaults={
                    'total_processed': stats['total_processed'] or 0,
                    'total_suspicious': stats['total_suspicious'] or 0,
                    'total_fraud': stats['total_fraud'] or 0,
                    'avg_processing_time': stats['avg_processing_time'] or 0.0
                }
            )
            
            self.logger.info(f"📊 Daily stats updated for {today}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating daily stats: {e}")
            return False
    
    def get_system_overview(self):
        """Возвращает обзор статистики системы"""
        today = datetime.now().date()
        
        try:
            today_stats = SystemStats.objects.filter(date=today).first()
            total_transactions = Transaction.objects.count()
            active_rules_count = FraudRule.objects.filter(is_active=True).count()
            
            # Статистика за последние 7 дней
            week_ago = today - timedelta(days=7)
            recent_stats = SystemStats.objects.filter(date__gte=week_ago).order_by('date')
            
            overview = {
                'today': {
                    'processed': today_stats.total_processed if today_stats else 0,
                    'suspicious': today_stats.total_suspicious if today_stats else 0,
                    'fraud': today_stats.total_fraud if today_stats else 0,
                },
                'total_transactions': total_transactions,
                'active_rules': active_rules_count,
                'recent_trend': [
                    {
                        'date': stat.date.isoformat(),
                        'processed': stat.total_processed,
                        'suspicious': stat.total_suspicious
                    }
                    for stat in recent_stats
                ]
            }
            
            return overview
            
        except Exception as e:
            self.logger.error(f"❌ Error getting system overview: {e}")
            return {}
    
    def generate_fraud_report(self, days=7):
        """Генерирует отчет по мошенническим операциям"""
        start_date = datetime.now().date() - timedelta(days=days)
        
        try:
            suspicious_transactions = Transaction.objects.filter(
                timestamp__date__gte=start_date,
                is_fraud=True
            ).select_related('fraud_check')
            
            report = {
                'period': f"Last {days} days",
                'total_fraud_cases': suspicious_transactions.count(),
                'total_amount_involved': sum(float(t.amount) for t in suspicious_transactions),
                'most_common_rules': self._get_most_common_rules(suspicious_transactions),
                'transactions': [
                    {
                        'id': str(t.id),
                        'correlation_id': str(t.correlation_id),
                        'amount': float(t.amount),
                        'timestamp': t.timestamp.isoformat(),
                        'triggered_rules': t.fraud_check.triggered_rules if hasattr(t, 'fraud_check') else []
                    }
                    for t in suspicious_transactions
                ]
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating fraud report: {e}")
            return {}
    
    def _get_most_common_rules(self, transactions):
        """Вспомогательный метод для определения самых частых сработавших правил"""
        rule_counter = {}
        
        for transaction in transactions:
            if hasattr(transaction, 'fraud_check'):
                for rule in transaction.fraud_check.triggered_rules:
                    rule_counter[rule] = rule_counter.get(rule, 0) + 1
        
        return sorted(rule_counter.items(), key=lambda x: x[1], reverse=True)[:5]