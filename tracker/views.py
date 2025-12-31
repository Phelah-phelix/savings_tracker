from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime, date
import calendar
from decimal import Decimal

from .models import MonthlyGoal, DailySaving

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Using Django's built-in UserCreationForm
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Authenticate the user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome {username}')
                return redirect('dashboard')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'tracker/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def dashboard(request):
    current_year = date.today().year
    current_month = date.today().month
    
    # Get or create current month goal
    current_goal, created = MonthlyGoal.objects.get_or_create(
        user=request.user,
        year=current_year,
        month=current_month,
        defaults={'goal_amount': 1000, 'motivation_text': 'Start saving!'}
    )
    
    # Get all monthly goals for current year
    monthly_goals = MonthlyGoal.objects.filter(
        user=request.user,
        year=current_year
    ).order_by('month')
    
    # Get savings for current month
    savings = DailySaving.objects.filter(
        monthly_goal=current_goal
    ).order_by('-date')[:10]
    
    # Get days for calendar
    days_in_month = calendar.monthrange(current_year, current_month)[1]
    days = []
    
    for day in range(1, days_in_month + 1):
        current_date = date(current_year, current_month, day)
        saving = DailySaving.objects.filter(
            monthly_goal=current_goal,
            date=current_date
        ).first()
        
        days.append({
            'date': current_date,
            'saving': saving,
            'day_number': day
        })
    
    # Calculate daily average needed
    days_passed = DailySaving.objects.filter(monthly_goal=current_goal).count()
    remaining_days = days_in_month - days_passed
    if remaining_days > 0:
        remaining_amount = max(Decimal('0.00'), current_goal.goal_amount - current_goal.total_saved())
        daily_average = remaining_amount / Decimal(str(remaining_days))
    else:
        daily_average = Decimal('0.00')
    
    context = {
        'current_goal': current_goal,
        'monthly_goals': monthly_goals,
        'savings': savings,
        'days': days,
        'daily_average': daily_average,
        'current_year': current_year,
        'current_month': current_month,
    }
    
    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_daily_saving(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        note = request.POST.get('note', '')
        saving_date = request.POST.get('date', date.today().isoformat())
        
        if not amount:
            messages.error(request, 'Please enter an amount.')
            return redirect('dashboard')
        
        try:
            saving_date_obj = date.fromisoformat(saving_date)
        except (ValueError, TypeError):
            saving_date_obj = date.today()
        
        # Get or create monthly goal for this date
        monthly_goal, created = MonthlyGoal.objects.get_or_create(
            user=request.user,
            year=saving_date_obj.year,
            month=saving_date_obj.month,
            defaults={'goal_amount': 1000}
        )
        
        # Check if saving already exists for this date
        existing_saving = DailySaving.objects.filter(
            monthly_goal=monthly_goal,
            date=saving_date_obj
        ).first()
        
        if existing_saving:
            existing_saving.amount = amount
            existing_saving.note = note
            existing_saving.save()
            messages.success(request, 'Saving updated successfully!')
        else:
            DailySaving.objects.create(
                monthly_goal=monthly_goal,
                date=saving_date_obj,
                amount=amount,
                note=note
            )
            messages.success(request, 'Saving added successfully!')
        
        return redirect('dashboard')
    
    return redirect('dashboard')

@login_required
def edit_monthly_goal(request, goal_id):
    goal = get_object_or_404(MonthlyGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        goal_amount = request.POST.get('goal_amount')
        motivation_text = request.POST.get('motivation_text', '')
        
        if goal_amount:
            try:
                goal.goal_amount = Decimal(goal_amount)
                goal.motivation_text = motivation_text
                goal.save()
                messages.success(request, 'Goal updated successfully!')
            except (ValueError, TypeError):
                messages.error(request, 'Please enter a valid amount.')
    
    return redirect('dashboard')

@login_required
def month_detail(request, year, month):
    monthly_goal = get_object_or_404(
        MonthlyGoal,
        user=request.user,
        year=year,
        month=month
    )
    
    # Get all days in month
    days_in_month = calendar.monthrange(year, month)[1]
    days = []
    
    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        saving = DailySaving.objects.filter(
            monthly_goal=monthly_goal,
            date=current_date
        ).first()
        
        days.append({
            'date': current_date,
            'saving': saving,
            'day_number': day
        })
    
    # Prepare data for chart
    chart_data = []
    cumulative = Decimal('0.00')
    
    for day in days:
        if day['saving']:
            cumulative += day['saving'].amount
        chart_data.append(float(cumulative))
    
    context = {
        'monthly_goal': monthly_goal,
        'days': days,
        'chart_data': chart_data,
        'month_name': calendar.month_name[month],
        'year': year,
        'month': month,
    }
    
    return render(request, 'tracker/month_detail.html', context)

# In tracker/views.py - Update the yearly_overview function:

@login_required
def yearly_overview(request, year=None):
    if year is None:
        year = date.today().year
    
    monthly_goals = MonthlyGoal.objects.filter(
        user=request.user,
        year=year
    ).order_by('month')
    
    # Create list of all months with actual or placeholder goals
    all_months = []
    total_goal = Decimal('0.00')
    total_saved = Decimal('0.00')
    
    for month_num in range(1, 13):
        try:
            goal = monthly_goals.get(month=month_num)
        except MonthlyGoal.DoesNotExist:
            # Create a placeholder goal that won't be saved to DB
            goal = MonthlyGoal(
                user=request.user,
                year=year,
                month=month_num,
                goal_amount=Decimal('0.00')
            )
            # Set pk to None to indicate it's not saved
            goal.pk = None
        
        all_months.append(goal)
        total_goal += goal.goal_amount
        
        # Only add to total_saved if goal exists in DB
        if goal.pk:
            total_saved += goal.total_saved()
    
    # Calculate yearly progress
    yearly_progress = (float(total_saved) / float(total_goal) * 100) if total_goal > 0 else 0
    
    context = {
        'year': year,
        'monthly_goals': all_months,
        'total_goal': total_goal,
        'total_saved': total_saved,
        'yearly_progress': yearly_progress,
        'yearly_variance': total_saved - total_goal,
    }
    
    return render(request, 'tracker/yearly_overview.html', context)

@login_required
def delete_saving(request, saving_id):
    saving = get_object_or_404(DailySaving, id=saving_id, monthly_goal__user=request.user)
    saving.delete()
    messages.success(request, 'Saving deleted successfully!')
    return redirect('dashboard')