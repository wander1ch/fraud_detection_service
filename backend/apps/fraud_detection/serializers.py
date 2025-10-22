from rest_framework import serializers
from .models import Transaction, Rule, Alert

class StatisticsSerializer(serializers.Serializer):
    fraud = serializers.IntegerField()
    normal = serializers.IntegerField()
    total = serializers.IntegerField()
    fraud_percentage = serializers.FloatField()