from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['amount', 'from_account', 'to_account']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_from_account(self, value):
        if not value.strip():
            raise serializers.ValidationError("From account cannot be empty")
        return value.strip()
    
    def validate_to_account(self, value):
        if not value.strip():
            raise serializers.ValidationError("To account cannot be empty")
        return value.strip()