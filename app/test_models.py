from django.test import TestCase
from app.models import Transaction, FraudRule
from app.test_factories import TransactionFactory, FraudRuleFactory

class TransactionModelTest(TestCase):
    """Тесты для модели Transaction"""
    
    def test_transaction_creation(self):
        """Тест создания транзакции"""
        transaction = Transaction.objects.create(
            amount=1000.00,
            from_account="user1",
            to_account="user2"
        )
        self.assertEqual(transaction.amount, 1000.00)
        self.assertEqual(transaction.status, 'pending')
        self.assertFalse(transaction.is_fraud)
        self.assertIsNotNone(transaction.correlation_id)
        print("✅ Тест создания транзакции пройден")
    
    def test_transaction_factory(self):
        """Тест фабрики транзакций"""
        transaction = TransactionFactory()
        self.assertIsInstance(transaction, Transaction)
        self.assertTrue(transaction.amount > 0)
        print("✅ Тест фабрики транзакций пройден")

class FraudRuleModelTest(TestCase):
    """Тесты для модели FraudRule"""
    
    def test_fraud_rule_creation(self):
        """Тест создания правила"""
        rule = FraudRule.objects.create(
            name="Большая сумма",
            rule_type="threshold",
            description="Транзакции больше 100,000",
            threshold_amount=100000.00
        )
        self.assertEqual(rule.name, "Большая сумма")
        self.assertEqual(rule.rule_type, "threshold")
        self.assertTrue(rule.is_active)
        print("✅ Тест создания правила пройден")
    
    def test_fraud_rule_factory(self):
        """Тест фабрики правил"""
        rule = FraudRuleFactory()
        self.assertIsInstance(rule, FraudRule)
        self.assertEqual(rule.rule_type, 'threshold')
        print("✅ Тест фабрики правил пройден")