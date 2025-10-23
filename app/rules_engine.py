import logging
from datetime import datetime, time
from .models import FraudRule

logger = logging.getLogger(__name__)

class RulesEngine:
    def __init__(self):
        self.rules = self._load_rules()
        logger.info(f"🎯 RulesEngine initialized with {len(self.rules)} active rules")
    
    def _load_rules(self):
        """Загружаем активные правила из базы данных"""
        try:
            rules = FraudRule.objects.filter(is_active=True)
            logger.info(f"📥 Loaded rules: {[rule.name for rule in rules]}")
            return rules
        except Exception as e:
            logger.error(f"❌ Error loading rules: {e}")
            return []
    
    def apply_rules(self, transaction_data):
        """Применяем все правила к транзакции"""
        results = {
            'is_fraud': False,
            'fraud_score': 0.0,
            'triggered_rules': [],
            'details': {}
        }
        
        amount = float(transaction_data.get('amount', 0))
        logger.info(f"💰 Processing transaction amount: {amount}")
        
        for rule in self.rules:
            logger.info(f"🔎 Applying rule: {rule.name} (type: {rule.rule_type})")
            rule_result = self._apply_single_rule(rule, transaction_data)
            if rule_result['triggered']:
                logger.info(f"🚨 Rule triggered: {rule.name} - {rule_result['reason']}")
                results['triggered_rules'].append(rule.name)
                results['fraud_score'] = max(results['fraud_score'], rule_result['score'])
                results['details'][rule.name] = rule_result['reason']
        
        # Если есть сработавшие правила, помечаем как мошенничество
        if results['triggered_rules']:
            results['is_fraud'] = True
            logger.info(f"🎯 Transaction marked as FRAUD. Score: {results['fraud_score']}")
        else:
            logger.info("✅ Transaction is CLEAN")
            
        return results
    
    def _apply_single_rule(self, rule, transaction_data):
        """Применяем одно правило к транзакции"""
        try:
            if rule.rule_type == 'threshold':
                return self._apply_threshold_rule(rule, transaction_data)
            elif rule.rule_type == 'pattern':
                return self._apply_pattern_rule(rule, transaction_data)
            elif rule.rule_type == 'composite':
                return self._apply_composite_rule(rule, transaction_data)
            elif rule.rule_type == 'ml':
                return self._apply_ml_rule(rule, transaction_data)
            else:
                return {'triggered': False, 'score': 0.0, 'reason': 'Unknown rule type'}
        except Exception as e:
            logger.error(f"Error applying rule {rule.name}: {e}")
            return {'triggered': False, 'score': 0.0, 'reason': f'Error: {str(e)}'}
    
    def _apply_threshold_rule(self, rule, transaction_data):
        """Пороговое правило: сумма > X"""
        amount = float(transaction_data.get('amount', 0))
        threshold = float(rule.threshold_amount or 0)
        
        logger.info(f"📊 Threshold rule check: {amount} > {threshold}")
        
        if amount > threshold:
            return {
                'triggered': True,
                'score': 0.7,
                'reason': f'Amount {amount} exceeds threshold {threshold}'
            }
        return {'triggered': False, 'score': 0.0, 'reason': ''}
    
    def _apply_pattern_rule(self, rule, transaction_data):
        """Правило паттернов (пока заглушка)"""
        # Здесь можно добавить логику для обнаружения паттернов
        # Например: серия малых транзакций за короткий период
        logger.info("🔍 Pattern rule check (not implemented)")
        return {'triggered': False, 'score': 0.0, 'reason': 'Pattern rule not implemented'}
    
    def _apply_composite_rule(self, rule, transaction_data):
        """Составное правило: большая сумма И ночное время"""
        amount = float(transaction_data.get('amount', 0))
        current_time = datetime.now().time()
    
        # Берем настройки из базы данных или используем значения по умолчанию
        nighttime_start = rule.nighttime_start or time(22, 0)  # 22:00 по умолчанию
        nighttime_end = rule.nighttime_end or time(6, 0)       # 06:00 по умолчанию
        amount_threshold = float(rule.composite_amount or 50000)  # 50,000 по умолчанию
    
        # Проверяем ночное время (учитываем, что ночь может переходить через полночь)
        if nighttime_start < nighttime_end:
        # Нормальный случай: 22:00-06:00
            is_nighttime = nighttime_start <= current_time <= nighttime_end
        else:
            # Ночь переходит через полночь: 22:00-06:00 следующего дня
            is_nighttime = (current_time >= nighttime_start) or (current_time <= nighttime_end)
    
        is_large_amount = amount > amount_threshold
    
        logger.info(f"🌙 Composite rule check: amount={amount}, threshold={amount_threshold}, "
                    f"nighttime={is_nighttime} ({nighttime_start}-{nighttime_end}), current_time={current_time}")
    
        if is_large_amount and is_nighttime:
            return {
                'triggered': True,
                'score': 0.8,
                'reason': f'Large amount {amount} at nighttime ({current_time})'
            }
        return {'triggered': False, 'score': 0.0, 'reason': ''}
    
    def _apply_ml_rule(self, rule, transaction_data):
        """ML правило (пока заглушка с простой логикой)"""
        amount = float(transaction_data.get('amount', 0))
        
        # Простая имитация ML модели
        ml_score = min(amount / 100000, 1.0)  # Чем больше сумма, тем выше score
        ml_threshold = float(rule.ml_threshold or 0.8)
        
        logger.info(f"🤖 ML rule check: score={ml_score:.2f}, threshold={ml_threshold}")
        
        if ml_score > ml_threshold:
            return {
                'triggered': True,
                'score': ml_score,
                'reason': f'ML score {ml_score:.2f} exceeds threshold {ml_threshold}'
            }
        return {'triggered': False, 'score': 0.0, 'reason': ''}