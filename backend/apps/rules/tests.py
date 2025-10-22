from django.test import TestCase
from django.test import Client
from django.utils import timezone
from .models import Rule
import json

class RuleEngineAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Создание тестовых правил
        self.threshold_rule = Rule.objects.create(
            name="High Amount Rule",
            type="threshold",
            condition=json.dumps({
                "field": "amount",
                "operator": ">",
                "value": 1000
            }),
            threshold=1000,
            active=True
        )

    def test_evaluate_transaction_api(self):
        """Тест API оценки транзакции"""
        transaction_data = {
            "transaction_id": "test_123",
            "amount": 1500,
            "user_id": "user_1",
            "timestamp": timezone.now().isoformat(),
            "currency": "USD"
        }
        
        response = self.client.post(
            '/rules/evaluate/',
            data=json.dumps(transaction_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['transaction_id'], 'test_123')
        self.assertGreater(data['data']['evaluation_result']['alerts_triggered'], 0)

    def test_evaluate_transaction_invalid_json(self):
        """Тест с невалидным JSON"""
        response = self.client.post(
            '/rules/evaluate/',
            data='invalid json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')

    def test_get_rules_api(self):
        """Тест API получения правил"""
        response = self.client.get('/rules/rules/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertIn('rules', data['data'])

    def test_health_check(self):
        """Тест health check endpoint"""
        response = self.client.get('/rules/health/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['service'], 'Rule Engine API')