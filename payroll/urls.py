from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('', views.employee_payroll_view, name='home'),
    path('admin-view/', views.admin_payroll_view, name='admin_payroll'),
    path('admin-view/update/<str:employee_id>/', views.admin_update_salary, name='admin_update_salary'),
    path('admin-view/generate/', views.admin_generate_payslip_view, name='admin_generate_payslip'),
    path('admin-view/pay/<int:payslip_id>/', views.admin_pay_payslip_view, name='admin_pay_payslip'),
]
