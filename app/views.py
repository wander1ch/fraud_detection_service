from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
import uuid
from .models import Transaction
from .serializers import TransactionSerializer  # Импорт из serializers.py
from .tasks import process_transaction
from .reporting import ReportingEngine
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .tasks import process_transaction_task, send_fraud_notification
class LoginView(View):
    def get(self, request):
        # Простая HTML страница входа
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Вход в систему</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 400px; margin: 0 auto; }
                .form-group { margin-bottom: 15px; }
                .form-control { width: 100%; padding: 8px; margin-top: 5px; }
                .btn { padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; width: 100%; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Вход в систему</h1>
                <form method="post">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">
                    <div class="form-group">
                        <label>Имя пользователя:</label>
                        <input type="text" name="username" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label>Пароль:</label>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                    <button type="submit" class="btn">Войти</button>
                </form>
                <div style="margin-top: 20px;">
                    <a href="/">← Назад на главную</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('app:home')
        
        # Если ошибка входа, покажем сообщение
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Вход в систему</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 400px; margin: 0 auto; }
                .error { color: red; margin-bottom: 15px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Вход в систему</h1>
                <div class="error">Неверное имя пользователя или пароль.</div>
                <a href="/login/">← Попробовать снова</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('app:home')

@method_decorator(csrf_exempt, name='dispatch')
class HomeView(View):
    def get(self, request):
        # Главная страница с правильным CSRF токеном
        from django.middleware.csrf import get_token
        csrf_token = get_token(request)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Fraud Detection System</title>
            <meta charset="UTF-8">
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                .dashboard {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-bottom: 30px;
                }}
                .card {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 10px;
                    border-left: 4px solid #3498db;
                }}
                .form-group {{ 
                    margin-bottom: 20px; 
                }}
                .form-control {{ 
                    width: 100%; 
                    padding: 12px; 
                    border: 1px solid #ddd; 
                    border-radius: 5px; 
                    font-size: 16px;
                }}
                .btn {{ 
                    padding: 12px 25px; 
                    background: #3498db; 
                    color: white; 
                    border: none; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    font-size: 16px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .btn:hover {{ 
                    background: #2980b9; 
                }}
                .nav-links {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 30px;
                }}
                .nav-links a {{
                    padding: 15px;
                    background: #f8f9fa;
                    color: #2c3e50;
                    text-decoration: none;
                    border-radius: 8px;
                    text-align: center;
                    transition: background 0.3s;
                }}
                .nav-links a:hover {{
                    background: #3498db;
                    color: white;
                }}
                @media (max-width: 768px) {{
                    .dashboard {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Fraud Detection System</h1>
                    <p>Система обнаружения мошеннических транзакций</p>
                </div>

                <div class="dashboard">
                    <div class="card">
                        <h2>💳 Создать транзакцию</h2>
                        <form method="post">
                            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                            <div class="form-group">
                                <label><strong>Сумма:</strong></label>
                                <input type="number" name="amount" class="form-control" step="0.01" min="0.01" placeholder="1000.00" required>
                            </div>
                            <div class="form-group">
                                <label><strong>От аккаунта:</strong></label>
                                <input type="text" name="from_account" class="form-control" placeholder="user123" required>
                            </div>
                            <div class="form-group">
                                <label><strong>К аккаунта:</strong></label>
                                <input type="text" name="to_account" class="form-control" placeholder="user456" required>
                            </div>
                            <button type="submit" class="btn" style="width: 100%;">📨 Создать транзакцию</button>
                        </form>
                    </div>

                    <div class="card">
                        <h2>📊 Информация</h2>
                        <p>Система готова к работе!</p>
                        <p>Создайте транзакцию для проверки на мошенничество.</p>
                        <p><strong>Тестовые данные:</strong></p>
                        <ul>
                            <li>Малая сумма: 1000 (не подозрительно)</li>
                            <li>Большая сумма: 150000 (подозрительно)</li>
                        </ul>
                    </div>
                </div>

                <div class="nav-links">
                    <a href="/admin/" target="_blank">⚙️ Админ-панель</a>
                    <a href="/api/docs/" target="_blank">📖 API Документация</a>
                    <a href="/api/transactions/list/" target="_blank">💰 Список транзакций</a>
                    <a href="/login/">🔐 Войти в систему</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    
    def post(self, request):
        # Обработка формы создания транзакции
        try:
            amount = request.POST.get('amount')
            from_account = request.POST.get('from_account')
            to_account = request.POST.get('to_account')
            
            # Создаем транзакцию
            transaction = Transaction.objects.create(
                amount=amount,
                from_account=from_account,
                to_account=to_account,
                status='pending'
            )
            
            # ЗАПУСКАЕМ АСИНХРОННУЮ ОБРАБОТКУ
            process_transaction_task.delay(transaction.id)
            
            message = f"""✅ Транзакция принята в обработку!

ID: {transaction.id}
Correlation ID: {transaction.correlation_id}
Статус: Обрабатывается...
Обработка выполняется асинхронно в фоновом режиме.

Обновите страницу через несколько секунд для получения результата."""
            
        except Exception as e:
            message = f"❌ Ошибка: {str(e)}"
            print(f"Ошибка при создании транзакции: {e}")
        
        # Показываем результат
        from django.middleware.csrf import get_token
        csrf_token = get_token(request)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Результат - Fraud Detection</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 800px; 
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                }}
                .result {{ 
                    margin-top: 20px; 
                    padding: 20px; 
                    border-radius: 8px; 
                }}
                .success {{ 
                    background: #d4edda; 
                    color: #155724; 
                    border-left: 4px solid #27ae60; 
                }}
                .error {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                    border-left: 4px solid #e74c3c; 
                }}
                .btn {{ 
                    padding: 10px 20px; 
                    background: #007cba; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    display: inline-block;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📋 Результат обработки</h1>
                <div class="result {'success' if '✅' in message else 'error'}">
                    <pre style="white-space: pre-wrap; font-family: inherit;">{message}</pre>
                </div>
                <div>
                    <a href="/" class="btn">← Создать еще транзакцию</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)

# API Views
@method_decorator(csrf_exempt, name='dispatch')
class TransactionCreateView(View):
    def post(self, request):
        # API endpoint для создания транзакции
        from django.http import JsonResponse
        import json
        
        try:
            data = json.loads(request.body)
            serializer = TransactionSerializer(data=data)
            
            if serializer.is_valid():
                transaction = serializer.save(
                    status='pending',
                    is_fraud=False,
                    fraud_score=0.0
                )
                
                # ЗАПУСКАЕМ АСИНХРОННУЮ ОБРАБОТКУ
                task = process_transaction_task.delay(transaction.id)
                
                return JsonResponse({
                    'id': str(transaction.id),
                    'correlation_id': str(transaction.correlation_id),
                    'status': 'processing',
                    'task_id': task.id,
                    'message': 'Transaction is being processed asynchronously'
                })
            
            return JsonResponse(serializer.errors, status=400)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class TransactionListView(View):
    def get(self, request):
        from django.http import JsonResponse
        transactions = Transaction.objects.all().order_by('-timestamp')[:10]
        data = []
        for transaction in transactions:
            data.append({
                'id': str(transaction.id),
                'correlation_id': str(transaction.correlation_id),
                'amount': str(transaction.amount),
                'from_account': transaction.from_account,
                'to_account': transaction.to_account,
                'status': transaction.status,
                'is_fraud': transaction.is_fraud,
                'timestamp': transaction.timestamp.isoformat()
            })
        return JsonResponse(data, safe=False)

# Остальные API views...
class TransactionDetailView(View):
    def get(self, request, id):
        from django.http import JsonResponse
        try:
            transaction = Transaction.objects.get(id=id)
            return JsonResponse({
                'id': str(transaction.id),
                'correlation_id': str(transaction.correlation_id),
                'amount': str(transaction.amount),
                'from_account': transaction.from_account,
                'to_account': transaction.to_account,
                'status': transaction.status,
                'is_fraud': transaction.is_fraud,
                'fraud_score': transaction.fraud_score,
                'timestamp': transaction.timestamp.isoformat()
            })
        except Transaction.DoesNotExist:
            return JsonResponse({'error': 'Transaction not found'}, status=404)

class SystemOverviewView(View):
    def get(self, request):
        from django.http import JsonResponse
        reporting_engine = ReportingEngine()
        overview = reporting_engine.get_system_overview()
        return JsonResponse(overview)

class FraudReportView(View):
    def get(self, request):
        from django.http import JsonResponse
        from .reporting import ReportingEngine
        days = int(request.GET.get('days', 7))
        reporting_engine = ReportingEngine()
        report = reporting_engine.generate_fraud_report(days)
        return JsonResponse(report)