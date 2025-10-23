import pytest
from django.core.exceptions import ValidationError
from app.models import Transaction, FraudRule
from .factories import TransactionFactory, FraudRuleFactory

class TestTransactionModel:
    """Тесты для модели Transaction"""
    
    def test_transaction_creation(self, transaction):
        """Тест создания транзакции"""
        assert transaction.amount > 0
        assert transaction.status == 'pending'
        assert transaction.is_fraud is False
        assert transaction.fraud_score == 0.0
        assert transaction.correlation_id is not None
    
    def test_transaction_string_representation(self, transaction):
        """Тест строкового представления транзакции"""
        expected_str = f"Transaction {transaction.correlation_id} - {transaction.amount}"
        assert str(transaction) == expected_str
    
    def test_transaction_ordering(self):
        """Тест ordering по timestamp"""
        # Создаем несколько транзакций
        transaction1 = TransactionFactory()
        transaction2 = TransactionFactory()
        
        transactions = Transaction.objects.all()
        # Последняя созданная должна быть первой (ordering = ['-timestamp'])
        assert transactions[0] == transaction2
        assert transactions[1] == transaction1

class TestFraudRuleModel:
    """Тесты для модели FraudRule"""
    
    def test_fraud_rule_creation(self, fraud_rule):
        """Тест создания правила"""
        assert fraud_rule.name is not None
        assert fraud_rule.rule_type == 'threshold'
        assert fraud_rule.is_active is True
    
    def test_fraud_rule_string_representation(self, fraud_rule):
        """Тест строкового представления правила"""
        expected_str = f"{fraud_rule.name} (Пороговое правило)"
        assert str(fraud_rule) == expected_str
    
    def test_threshold_rule_validation(self):
        """Тест валидации порогового правила"""
        rule = FraudRuleFactory(
            rule_type='threshold',
            threshold_amount=None  # Должна быть ошибка
        )
        
        with pytest.raises(ValidationError):
            rule.full_clean()
    
    @pytest.mark.parametrize("rule_type,expected_display", [
        ('threshold', 'Пороговое правило'),
        ('pattern', 'Паттерн'),
        ('composite', 'Составное правило'),
        ('ml', 'ML правило'),
    ])
    def test_rule_type_display(self, rule_type, expected_display):
        """Тест отображения типов правил"""
        rule = FraudRuleFactory(rule_type=rule_type)
        assert rule.get_rule_type_display() == expected_display