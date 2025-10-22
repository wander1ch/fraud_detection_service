from rest_framework import serializers
from apps.rules.models import Rule
from apps.transactions.models import Transactions as Transaction
from apps.notifications.models import Notification as Alert


class StatisticsSerializer(serializers.Serializer):
    fraud = serializers.IntegerField()
    normal = serializers.IntegerField()
    total = serializers.IntegerField()
    fraud_percentage = serializers.FloatField()