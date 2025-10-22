from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class RulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.rules' 
    verbose_name = 'Rule Engine'

    def ready(self):
        """Initialize rule engine when app is ready"""
        try:
            from .rules_engine import RuleEngine
            logger.info("Rule Engine app initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Rule Engine: {e}")
