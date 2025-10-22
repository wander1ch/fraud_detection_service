from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health_check, name="fraud_detection_health"),
]
from django.urls import path
from . import views
from .views import StatisticsAPIView

urlpatterns = [
    # Rules CRUD
    path('rules/', views.RuleListView.as_view(), name='rule_list'),
    path('rules/create/', views.RuleCreateView.as_view(), name='rule_create'),
    path('rules/<int:pk>/edit/', views.RuleUpdateView.as_view(), name='rule_edit'),
    path('rules/<int:pk>/delete/', views.RuleDeleteView.as_view(), name='rule_delete'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/export/', views.export_transactions_csv, name='export_transactions'),

    # Statistics
    path('statistics/', views.statistics_view, name='statistics'),

    # API
    path('api/statistics/', StatisticsAPIView.as_view(), name='api_statistics'),
]