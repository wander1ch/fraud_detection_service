from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import time
from .models import Rule, Alert, RuleMetrics
from .rule_engine import RuleEngine
from django.db import transaction

rule_engine = RuleEngine()

@method_decorator(csrf_exempt, name='dispatch')
class EvaluateTransactionView(View):
    """
    API endpoint для оценки транзакции по правилам
    Принимает JSON с данными транзакции
    Возвращает JSON с результатами оценки
    """
    
    def post(self, request):
        try:
            # Парсинг JSON из тела запроса
            data = json.loads(request.body.decode('utf-8'))
            
            # Валидация обязательных полей
            required_fields = ['transaction_id', 'amount', 'user_id', 'timestamp']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS'
                }, status=400)
            
            # Оценка транзакции по правилам
            start_time = time.time()
            alerts = rule_engine.evaluate_transaction(data)
            processing_time = time.time() - start_time
            
            # Формирование ответа
            response_data = {
                'status': 'success',
                'data': {
                    'transaction_id': data['transaction_id'],
                    'evaluation_result': {
                        'alerts_triggered': len(alerts),
                        'is_suspicious': len(alerts) > 0,
                        'processing_time_seconds': round(processing_time, 4)
                    },
                    'alerts': [
                        {
                            'alert_id': alert.id,
                            'rule_id': alert.rule.id,
                            'rule_name': alert.rule.name,
                            'rule_type': alert.rule.type,
                            'reason': alert.reason,
                            'severity': alert.severity,
                            'triggered_at': alert.created_at.isoformat()
                        } for alert in alerts
                    ]
                }
            }
            
            return JsonResponse(response_data, status=200)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format in request body',
                'code': 'INVALID_JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Internal server error: {str(e)}',
                'code': 'INTERNAL_ERROR'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RuleManagementView(View):
    """
    API для управления правилами
    """
    
    def get(self, request):
        """Получить все правила (JSON)"""
        try:
            rules = Rule.objects.filter(active=True)
            rules_data = []
            
            for rule in rules:
                rules_data.append({
                    'id': rule.id,
                    'name': rule.name,
                    'type': rule.type,
                    'condition': rule.condition,
                    'threshold': rule.threshold,
                    'active': rule.active,
                    'created_at': rule.created_at.isoformat(),
                    'updated_at': rule.updated_at.isoformat(),
                })
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'rules': rules_data,
                    'total_count': len(rules_data)
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'code': 'RULES_FETCH_ERROR'
            }, status=500)
    
    def post(self, request):
        """Создать новое правило (JSON input)"""
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            # Валидация обязательных полей
            required_fields = ['name', 'type', 'condition']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Missing required fields: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS'
                }, status=400)
            
            # Создание правила
            rule = Rule.objects.create(
                name=data['name'],
                type=data['type'],
                condition=data['condition'],
                threshold=data.get('threshold'),
                active=data.get('active', True)
            )
            
            # Создание метрик для нового правила
            RuleMetrics.objects.create(rule=rule)
            
            # Перезагрузка правил в движке
            rule_engine.load_rules()
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'rule_id': rule.id,
                    'message': 'Rule created successfully'
                }
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON format',
                'code': 'INVALID_JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'code': 'RULE_CREATION_ERROR'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class RuleDetailView(View):
    """API для работы с конкретным правилом"""
    
    def get(self, request, rule_id):
        """Получить правило по ID"""
        try:
            rule = Rule.objects.get(id=rule_id)
            
            return JsonResponse({
                'status': 'success',
                'data': {
                    'rule': {
                        'id': rule.id,
                        'name': rule.name,
                        'type': rule.type,
                        'condition': rule.condition,
                        'threshold': rule.threshold,
                        'active': rule.active,
                        'created_at': rule.created_at.isoformat(),
                        'updated_at': rule.updated_at.isoformat(),
                    }
                }
            })
            
        except Rule.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Rule not found',
                'code': 'RULE_NOT_FOUND'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e),
                'code': 'RULE_FETCH_ERROR'
            }, status=500)

@csrf_exempt
def get_metrics(request):
    """Получить метрики Rule Engine (JSON)"""
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        }, status=405)
    
    try:
        metrics = RuleMetrics.objects.select_related('rule').all()
        
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'rule_id': metric.rule.id,
                'rule_name': metric.rule.name,
                'evaluations_count': metric.evaluations_count,
                'triggers_count': metric.triggers_count,
                'avg_processing_time_ms': round(metric.avg_processing_time * 1000, 2),
                'trigger_ratio': round(metric.triggers_count / metric.evaluations_count, 4) if metric.evaluations_count > 0 else 0,
                'last_evaluated': metric.last_evaluated.isoformat(),
            })
        
        total_alerts = Alert.objects.count()
        active_rules = Rule.objects.filter(active=True).count()
        total_rules = Rule.objects.count()
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'summary': {
                    'total_alerts': total_alerts,
                    'active_rules': active_rules,
                    'total_rules': total_rules
                },
                'rule_metrics': metrics_data
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'code': 'METRICS_FETCH_ERROR'
        }, status=500)

@csrf_exempt
def get_alerts(request):
    """Получить алерты (JSON)"""
    if request.method != 'GET':
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed',
            'code': 'METHOD_NOT_ALLOWED'
        }, status=405)
    
    try:
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        alerts = Alert.objects.select_related('rule').order_by('-created_at')[offset:offset + limit]
        total_alerts = Alert.objects.count()
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'transaction_id': alert.transaction_id,
                'rule_id': alert.rule.id,
                'rule_name': alert.rule.name,
                'rule_type': alert.rule.type,
                'reason': alert.reason,
                'severity': alert.severity,
                'created_at': alert.created_at.isoformat(),
                'transaction_data': alert.transaction_data
            })
        
        return JsonResponse({
            'status': 'success',
            'data': {
                'alerts': alerts_data,
                'pagination': {
                    'total': total_alerts,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_alerts
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e),
            'code': 'ALERTS_FETCH_ERROR'
        }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """Health check endpoint"""
    
    def get(self, request):
        return JsonResponse({
            'status': 'success',
            'data': {
                'service': 'Rule Engine API',
                'status': 'healthy',
                'active_rules': Rule.objects.filter(active=True).count(),
                'total_alerts': Alert.objects.count(),
                'timestamp': time.time()
            }
        })