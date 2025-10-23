from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from app.models import Transaction
from app.test_factories import TransactionFactory

class TransactionAPITest(APITestCase):
    """Тесты API endpoints"""
    
    def test_create_transaction_success(self):
        """Тест успешного создания транзакции"""
        url = reverse('app:transaction-create')
        data = {
            'amount': '1500.00',
            'from_account': 'test_user_1',
            'to_account': 'test_user_2'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('correlation_id', response.data)
        self.assertIn('status', response.data)
        print("✅ Тест успешного создания транзакции пройден")
    
    def test_create_transaction_invalid_data(self):
        """Тест создания транзакции с невалидными данными"""
        url = reverse('app:transaction-create')
        data = {
            'amount': '-100.00',  # Отрицательная сумма
            'from_account': 'user1',
            'to_account': 'user2'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
        print("✅ Тест невалидных данных пройден")
    
    def test_get_transaction_detail(self):
        """Тест получения деталей транзакции"""
        # Создаем транзакцию
        transaction = TransactionFactory()
        
        url = reverse('app:transaction-detail', kwargs={'id': transaction.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(transaction.id))
        print("✅ Тест получения деталей транзакции пройден")
    
    def test_get_transaction_list(self):
        """Тест получения списка транзакций"""
        # Создаем несколько транзакций
        TransactionFactory()
        TransactionFactory()
        
        url = reverse('app:transaction-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        print("✅ Тест получения списка транзакций пройден")