import time
import logging
from decimal import Decimal
from .rules_engine import RulesEngine
from .models import FraudCheckResult, Transaction
from .reporting import ReportingEngine
from celery import shared_task
from celery.utils.log import get_task_logger


logger = logging.getLogger(__name__)

def process_transaction(transaction_data):
    """
    Обработка транзакции с использованием движка правил
    """
    try:
        logger.info(f"🚀 Starting transaction processing: {transaction_data}")
        
        # Имитация обработки
        time.sleep(1)
        
        # Используем движок правил для проверки
        rules_engine = RulesEngine()
        logger.info(f"📋 Loaded {len(rules_engine.rules)} active rules")
        
        fraud_result = rules_engine.apply_rules(transaction_data)
        logger.info(f"🔍 Fraud detection result: {fraud_result}")
        
        # Сохраняем результат проверки
        try:
            transaction = Transaction.objects.get(id=transaction_data['id'])
            
            # Создаем запись о результате проверки
            FraudCheckResult.objects.create(
                transaction=transaction,
                total_rules_checked=len(rules_engine.rules),
                triggered_rules=fraud_result['triggered_rules'],
                final_score=fraud_result['fraud_score'],
                details=fraud_result['details']
            )
            
            # Обновляем статистику
            reporting_engine = ReportingEngine()
            reporting_engine.update_daily_stats()
            
        except Exception as e:
            logger.error(f"❌ Error saving fraud check result: {e}")
        
        result = {
            'transaction_id': transaction_data.get('id'),
            'is_fraud': fraud_result['is_fraud'],
            'fraud_score': float(round(fraud_result['fraud_score'], 2)),
            'triggered_rules': fraud_result['triggered_rules'],
            'details': fraud_result['details'],
            'status': 'suspicious' if fraud_result['is_fraud'] else 'completed'
        }
        
        logger.info(f"✅ Transaction processed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Error processing transaction: {str(e)}")
        raise

@shared_task(bind=True, max_retries=3)
def process_transaction_task(self, transaction_id):
    """
    Асинхронная задача для обработки транзакции
    """
    try:
        logger.info(f"🚀 Starting async processing for transaction {transaction_id}")
        
        # Получаем транзакцию
        transaction = Transaction.objects.get(id=transaction_id)
        transaction.status = 'processing'
        transaction.save()
        
        # Подготовка данных для движка правил
        transaction_data = {
            'id': str(transaction.id),
            'correlation_id': str(transaction.correlation_id),
            'amount': float(transaction.amount),
            'from_account': transaction.from_account,
            'to_account': transaction.to_account
        }
        
        # Используем движок правил для проверки
        rules_engine = RulesEngine()
        fraud_result = rules_engine.apply_rules(transaction_data)
        
        logger.info(f"🔍 Fraud detection result: {fraud_result}")
        
        # Сохраняем результат проверки
        FraudCheckResult.objects.create(
            transaction=transaction,
            total_rules_checked=len(rules_engine.rules),
            triggered_rules=fraud_result['triggered_rules'],
            final_score=fraud_result['fraud_score'],
            details=fraud_result['details']
        )
        
        # Обновляем транзакцию
        transaction.status = 'suspicious' if fraud_result['is_fraud'] else 'completed'
        transaction.is_fraud = fraud_result['is_fraud']
        transaction.fraud_score = fraud_result['fraud_score']
        transaction.save()
        
        # Обновляем статистику
        reporting_engine = ReportingEngine()
        reporting_engine.update_daily_stats()
        
        # Если обнаружено мошенничество, можно отправить уведомление
        if fraud_result['is_fraud']:
            logger.warning(f"🚨 Fraud detected in transaction {transaction_id}")
            # Здесь можно добавить отправку уведомлений
            # send_fraud_notification.delay(transaction_id)
        
        result = {
            'transaction_id': transaction_id,
            'is_fraud': fraud_result['is_fraud'],
            'fraud_score': fraud_result['fraud_score'],
            'triggered_rules': fraud_result['triggered_rules'],
            'status': transaction.status
        }
        
        logger.info(f"✅ Transaction {transaction_id} processed successfully")
        return result
        
    except Transaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error processing transaction {transaction_id}: {str(e)}")
        # Повторяем задачу через 60 секунд
        raise self.retry(exc=e, countdown=60)

@shared_task
def batch_process_transactions(transaction_ids):
    """
    Пакетная обработка нескольких транзакций
    """
    results = []
    for transaction_id in transaction_ids:
        result = process_transaction_task.delay(transaction_id)
        results.append(result)
    return results

@shared_task
def cleanup_old_transactions(days=30):
    """
    Очистка старых транзакций (архивация)
    """
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_date = timezone.now() - timedelta(days=days)
    old_transactions = Transaction.objects.filter(timestamp__lt=cutoff_date)
    
    count = old_transactions.count()
    old_transactions.delete()
    
    logger.info(f"🧹 Cleaned up {count} transactions older than {days} days")
    return count

@shared_task
def generate_daily_report():
    """
    Генерация ежедневного отчета
    """
    from .reporting import ReportingEngine
    reporting_engine = ReportingEngine()
    
    # Обновляем статистику
    reporting_engine.update_daily_stats()
    
    # Генерируем отчет
    report = reporting_engine.generate_fraud_report(1)
    
    logger.info("📊 Daily report generated")
    return report

@shared_task
def send_fraud_notification(transaction_id):
    """
    Отправка уведомления о подозрительной транзакции
    """
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        
        # Здесь можно интегрировать с email, SMS, Telegram и т.д.
        message = f"""
        🚨 ОБНАРУЖЕНА ПОДОЗРИТЕЛЬНАЯ ТРАНЗАКЦИЯ
        
        ID: {transaction.correlation_id}
        Сумма: {transaction.amount}
        От: {transaction.from_account}
        К: {transaction.to_account}
        Время: {transaction.timestamp}
        Fraud Score: {transaction.fraud_score}
        """
        
        # Пример отправки в лог (замените на реальную интеграцию)
        logger.warning(f"FRAUD ALERT: {message}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sending fraud notification: {e}")
        return False