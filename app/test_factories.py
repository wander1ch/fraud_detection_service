import factory
from django.utils import timezone
from app.models import Transaction, FraudRule, FraudCheckResult, SystemStats
import uuid

class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction
    
    id = factory.LazyFunction(uuid.uuid4)
    amount = 1000.00
    from_account = "test_user_1"
    to_account = "test_user_2"
    status = 'pending'
    correlation_id = factory.LazyFunction(uuid.uuid4)
    is_fraud = False
    fraud_score = 0.0

class FraudRuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FraudRule
    
    name = "Test Rule"
    rule_type = 'threshold'
    description = "Test description"
    is_active = True
    threshold_amount = 100000.00