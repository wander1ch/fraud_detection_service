from django.test import TestCase
from app.serializers import TransactionSerializer

class TransactionSerializerTest(TestCase):
    """Тесты для TransactionSerializer"""
    
    def test_valid_serializer(self):
        """Тест валидных данных"""
        data = {
            'amount': '5000.00',
            'from_account': 'user123',
            'to_account': 'user456'
        }
        serializer = TransactionSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['amount'], 5000.00)
        self.assertEqual(serializer.validated_data['from_account'], 'user123')
        print("✅ Тест валидного сериализатора пройден")
    
    def test_invalid_negative_amount(self):
        """Тест отрицательной суммы"""
        data = {
            'amount': '-100.00',
            'from_account': 'user123',
            'to_account': 'user456'
        }
        serializer = TransactionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('amount', serializer.errors)
        print("✅ Тест отрицательной суммы пройден")
    
    def test_invalid_empty_accounts(self):
        """Тест пустых аккаунтов"""
        data = {
            'amount': '1000.00',
            'from_account': '',
            'to_account': 'user456'
        }
        serializer = TransactionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('from_account', serializer.errors)
        print("✅ Тест пустых аккаунтов пройден")