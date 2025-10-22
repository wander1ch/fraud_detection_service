import json
from datetime import datetime
from django.utils import timezone
from .models import Rule, Alert, RuleMetrics
import logging

logger = logging.getLogger(__name__)

class MLService:
    """Mock ML service for fraud detection"""
    
    def predict_fraud_probability(self, transaction_data):
        """
        Predict fraud probability (mock implementation)
        """
        base_prob = 0.01
        
        # Simple heuristic rules
        amount = transaction_data.get('amount', 0)
        if amount > 1000:
            base_prob += 0.3
        if amount > 5000:
            base_prob += 0.4
            
        # Nighttime transactions
        timestamp = transaction_data.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    transaction_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    transaction_time = datetime.now()
            else:
                transaction_time = timestamp
                
            if 0 <= transaction_time.hour < 6:  # 12 AM - 6 AM
                base_prob += 0.2
        
        # New user flag
        if transaction_data.get('is_new_user'):
            base_prob += 0.1
            
        # International transaction
        if transaction_data.get('is_international'):
            base_prob += 0.15
        
        return min(base_prob, 0.95)

class RuleEngine:
    def __init__(self):
        self.rules = []
        self.ml_service = MLService()
        self.load_rules()
    
    def load_rules(self):
        """Load active rules from database"""
        self.rules = list(Rule.objects.filter(active=True))
        logger.info(f"Loaded {len(self.rules)} active rules")
    
    def evaluate_transaction(self, transaction_data):
        """
        Evaluate transaction against all rules
        Returns list of created alerts
        """
        alerts = []
        
        for rule in self.rules:
            try:
                # Update metrics
                metrics, _ = RuleMetrics.objects.get_or_create(rule=rule)
                metrics.evaluations_count += 1
                
                start_time = timezone.now()
                rule_triggered = self._evaluate_single_rule(rule, transaction_data)
                processing_time = (timezone.now() - start_time).total_seconds()
                
                # Update average processing time
                total_time = metrics.avg_processing_time * (metrics.evaluations_count - 1) + processing_time
                metrics.avg_processing_time = total_time / metrics.evaluations_count
                
                if rule_triggered:
                    metrics.triggers_count += 1
                    alert = self._create_alert(rule, transaction_data)
                    alerts.append(alert)
                
                metrics.save()
                
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                continue
        
        return alerts
    
    def _evaluate_single_rule(self, rule, transaction_data):
        """Evaluate a single rule against transaction data"""
        
        if rule.type == 'threshold':
            return self._evaluate_threshold_rule(rule, transaction_data)
        elif rule.type == 'composite':
            return self._evaluate_composite_rule(rule, transaction_data)
        elif rule.type == 'ml_based':
            return self._evaluate_ml_rule(rule, transaction_data)
        else:
            logger.warning(f"Unknown rule type: {rule.type}")
            return False
    
    def _evaluate_threshold_rule(self, rule, transaction_data):
        """Evaluate threshold-based rules"""
        condition = rule.condition
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        transaction_value = transaction_data.get(field)
        
        if transaction_value is None:
            return False
        
        try:
            transaction_value = float(transaction_value)
            value = float(value)
            
            if operator == '>':
                return transaction_value > value
            elif operator == '>=':
                return transaction_value >= value
            elif operator == '<':
                return transaction_value < value
            elif operator == '<=':
                return transaction_value <= value
            elif operator == '==':
                return transaction_value == value
            else:
                logger.warning(f"Unknown operator: {operator}")
                return False
                
        except (ValueError, TypeError) as e:
            logger.error(f"Error comparing values: {e}")
            return False
    
    def _evaluate_composite_rule(self, rule, transaction_data):
        """Evaluate composite rules with AND/OR logic"""
        condition = rule.condition
        logic = condition.get('logic', 'AND').upper()
        conditions = condition.get('conditions', [])
        
        if logic == 'AND':
            return all(self._evaluate_condition(cond, transaction_data) for cond in conditions)
        elif logic == 'OR':
            return any(self._evaluate_condition(cond, transaction_data) for cond in conditions)
        else:
            logger.warning(f"Unknown logic operator: {logic}")
            return False
    
    def _evaluate_condition(self, condition, transaction_data):
        """Evaluate individual condition in composite rule"""
        condition_type = condition.get('type')
        
        if condition_type == 'amount_threshold':
            amount = transaction_data.get('amount', 0)
            threshold = condition.get('threshold', 0)
            operator = condition.get('operator', '>')
            
            if operator == '>':
                return amount > threshold
            elif operator == '>=':
                return amount >= threshold
        
        elif condition_type == 'nighttime':
            timestamp = transaction_data.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    try:
                        transaction_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        return False
                else:
                    transaction_time = timestamp
                
                return 0 <= transaction_time.hour < 6  # 12 AM - 6 AM
        
        elif condition_type == 'user_country':
            user_country = transaction_data.get('user_country', '')
            target_country = condition.get('country', '')
            return user_country == target_country
        
        elif condition_type == 'transaction_type':
            transaction_type = transaction_data.get('transaction_type', '')
            target_type = condition.get('transaction_type', '')
            return transaction_type == target_type
            
        elif condition_type == 'is_new_user':
            return transaction_data.get('is_new_user', False)
            
        elif condition_type == 'is_international':
            return transaction_data.get('is_international', False)
        
        return False
    
    def _evaluate_ml_rule(self, rule, transaction_data):
        """Evaluate ML-based rules"""
        fraud_probability = self.ml_service.predict_fraud_probability(transaction_data)
        threshold = rule.threshold or 0.5
        return fraud_probability > threshold
    
    def _create_alert(self, rule, transaction_data):
        """Create alert record in database"""
        reason = f"Rule '{rule.name}' triggered"
        
        # Determine severity based on rule type and conditions
        if rule.type == 'ml_based':
            severity = 'high'
        elif rule.type == 'composite':
            severity = 'medium'
        else:
            severity = 'low'
        
        alert = Alert.objects.create(
            rule=rule,
            transaction_id=transaction_data.get('transaction_id', 'unknown'),
            reason=reason,
            severity=severity,
            transaction_data=transaction_data
        )
        
        logger.info(f"Alert created: {alert.id} for rule {rule.name}")
        return alert