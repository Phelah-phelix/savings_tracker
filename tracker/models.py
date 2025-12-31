from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import calendar

class MonthlyGoal(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_goals')
    year = models.IntegerField(default=2024)
    month = models.IntegerField(choices=MONTH_CHOICES)
    goal_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        default=0.00
    )
    motivation_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'year', 'month']
        ordering = ['year', 'month']
    
    def __str__(self):
        return f"{self.get_month_display()} {self.year} - {self.user.username}"
    
    def total_saved(self):
        total = self.dailysaving_set.aggregate(total=models.Sum('amount'))['total']
        return total if total else Decimal('0.00')
    
    
    def progress_percentage(self):
        if self.goal_amount == 0:
            return 0
        return min(100, (float(self.total_saved()) / float(self.goal_amount)) * 100)
    
    def variance(self):
        return self.total_saved() - self.goal_amount
    
    def days_in_month(self):
        return calendar.monthrange(self.year, self.month)[1]

class DailySaving(models.Model):
    monthly_goal = models.ForeignKey(MonthlyGoal, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['monthly_goal', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.date}: Ksh{self.amount}"
    
    def day_of_month(self):
        return self.date.day