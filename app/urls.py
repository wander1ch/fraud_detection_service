from django.urls import path
from .views import (
    TransactionCreateView, TransactionDetailView, TransactionListView,
    SystemOverviewView, FraudReportView, HomeView, LoginView, LogoutView
)

app_name = 'app'

urlpatterns = [
    # Главная страница - должна обрабатывать GET и POST
    path('', HomeView.as_view(), name='home'),
    
    # Аутентификация
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # API endpoints
    path('api/transactions/', TransactionCreateView.as_view(), name='transaction-create'),
    path('api/transactions/list/', TransactionListView.as_view(), name='transaction-list'),
    path('api/transactions/<uuid:id>/', TransactionDetailView.as_view(), name='transaction-detail'),
    path('api/reports/overview/', SystemOverviewView.as_view(), name='system-overview'),
    path('api/reports/fraud/', FraudReportView.as_view(), name='fraud-report'),
]