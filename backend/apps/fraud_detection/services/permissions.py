from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q


def setup_groups():
    # Создаем группы
    admin_group, created = Group.objects.get_or_create(name='Admin')
    analyst_group, created = Group.objects.get_or_create(name='Analyst')

    # Получаем все permissions
    content_types = ContentType.objects.filter(
        Q(app_label='fraud_detection') | Q(app_label='auth')
    )

    # Admin получает все права
    admin_group.permissions.set(Permission.objects.filter(content_type__in=content_types))

    # Analyst получает только права на просмотр
    view_permissions = Permission.objects.filter(
        content_type__in=content_types,
        codename__in=['view_transaction', 'view_rule', 'view_alert']
    )
    analyst_group.permissions.set(view_permissions)