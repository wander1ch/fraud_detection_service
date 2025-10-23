from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'from_account', 'to_account']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'from_account': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'user123'
            }),
            'to_account': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'user456'
            }),
        }
        labels = {
            'amount': 'Сумма',
            'from_account': 'От аккаунта',
            'to_account': 'К аккаунту',
        }
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError("Сумма должна быть положительной")
        return amount
    
    def clean_from_account(self):
        from_account = self.cleaned_data['from_account']
        if not from_account.strip():
            raise forms.ValidationError("Аккаунт отправителя не может быть пустым")
        return from_account.strip()
    
    def clean_to_account(self):
        to_account = self.cleaned_data['to_account']
        if not to_account.strip():
            raise forms.ValidationError("Аккаунт получателя не может быть пустым")
        return to_account.strip()