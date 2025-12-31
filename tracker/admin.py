from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MonthlyGoal, DailySaving

@admin.register(MonthlyGoal)
class MonthlyGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'year', 'month', 'goal_amount', 'total_saved', 'progress_percentage']
    list_filter = ['year', 'month', 'user']
    search_fields = ['user__username', 'motivation_text']

@admin.register(DailySaving)
class DailySavingAdmin(admin.ModelAdmin):
    list_display = ['monthly_goal', 'date', 'amount', 'note']
    list_filter = ['date', 'monthly_goal__month']
    search_fields = ['note', 'monthly_goal__user__username']
    date_hierarchy = 'date'