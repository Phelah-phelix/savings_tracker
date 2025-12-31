from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MonthlyGoal, DailySaving
import datetime

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

class MonthlyGoalForm(forms.ModelForm):
    class Meta:
        model = MonthlyGoal
        fields = ['year', 'month', 'goal_amount', 'motivation_text']
        widgets = {
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': 2100
            }),
            'month': forms.Select(attrs={'class': 'form-control'}),
            'goal_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'motivation_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What motivates you to save this month?'
            }),
        }

class DailySavingForm(forms.ModelForm):
    class Meta:
        model = DailySaving
        fields = ['date', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'max': datetime.date.today().isoformat()
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional note about your saving...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['date'].initial = datetime.date.today()