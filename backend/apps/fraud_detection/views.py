from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok", "component": "fraud_detection"})


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Rule, Transaction, Alert
import csv
from django.http import HttpResponse
from django.db.models import Count, Q


class RuleListView(LoginRequiredMixin, ListView):
    model = Rule
    template_name = 'rules/rule_list.html'
    context_object_name = 'rules'


class RuleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Rule
    template_name = 'rules/rule_form.html'
    fields = ['name', 'description', 'condition', 'is_active']
    success_url = reverse_lazy('rule_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class RuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Rule
    template_name = 'rules/rule_form.html'
    fields = ['name', 'description', 'condition', 'is_active']
    success_url = reverse_lazy('rule_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class RuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Rule
    template_name = 'rules/rule_confirm_delete.html'
    success_url = reverse_lazy('rule_list')

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.all()
        fraud_filter = self.request.GET.get('fraud')

        if fraud_filter in ['0', '1']:
            queryset = queryset.filter(is_fraud=bool(int(fraud_filter)))

        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_count'] = self.get_queryset().count()
        context['fraud_count'] = self.get_queryset().filter(is_fraud=True).count()
        context['normal_count'] = self.get_queryset().filter(is_fraud=False).count()
        return context


def export_transactions_csv(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Amount', 'Timestamp', 'Is Fraud', 'Status', 'User'])

    transactions = Transaction.objects.all()
    for transaction in transactions:
        writer.writerow([
            transaction.id,
            transaction.amount,
            transaction.timestamp,
            'Yes' if transaction.is_fraud else 'No',
            transaction.status,
            transaction.user.username if transaction.user else 'N/A'
        ])

    return response


def statistics_view(request):
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    fraud_count = Transaction.objects.filter(is_fraud=True).count()
    normal_count = Transaction.objects.filter(is_fraud=False).count()
    total_count = Transaction.objects.count()

    # Статистика по сработавшим правилам
    rule_stats = Alert.objects.values('rule__name').annotate(
        count=Count('id')
    ).order_by('-count')

    context = {
        'fraud_count': fraud_count,
        'normal_count': normal_count,
        'total_count': total_count,
        'fraud_percentage': (fraud_count / total_count * 100) if total_count > 0 else 0,
        'rule_stats': rule_stats,
    }

    return render(request, 'statistics/statistics.html', context)
class AnalystRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Admin', 'Analyst']).exists()

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import StatisticsSerializer


class StatisticsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fraud_count = Transaction.objects.filter(is_fraud=True).count()
        normal_count = Transaction.objects.filter(is_fraud=False).count()
        total_count = Transaction.objects.count()

        data = {
            'fraud': fraud_count,
            'normal': normal_count,
            'total': total_count,
            'fraud_percentage': (fraud_count / total_count * 100) if total_count > 0 else 0
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)