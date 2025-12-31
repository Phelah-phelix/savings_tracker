from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),  # Changed from register to register_view
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Savings URLs
    path('add-saving/', views.add_daily_saving, name='add_daily_saving'),
    path('edit-goal/<int:goal_id>/', views.edit_monthly_goal, name='edit_monthly_goal'),
    path('delete-saving/<int:saving_id>/', views.delete_saving, name='delete_saving'),
    
    # View URLs
    path('month/<int:year>/<int:month>/', views.month_detail, name='month_detail'),
    path('year/<int:year>/', views.yearly_overview, name='yearly_overview'),
    path('yearly/', views.yearly_overview, name='yearly_overview_default'),
]