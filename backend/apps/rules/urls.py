from django.urls import path
from . import views

urlpatterns = [
    # Основные API endpoints
    path('evaluate/', views.EvaluateTransactionView.as_view(), name='evaluate_transaction'),
    path('rules/', views.RuleManagementView.as_view(), name='rule_management'),
    path('rules/<int:rule_id>/', views.RuleDetailView.as_view(), name='rule_detail'),
    path('metrics/', views.get_metrics, name='rule_metrics'),
    path('alerts/', views.get_alerts, name='rule_alerts'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
]