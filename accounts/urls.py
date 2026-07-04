from django.urls import path
from . import views

urlpatterns = [
    path('create-employee/', views.signup_view, name='create_employee'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/<int:profile_id>/edit/', views.edit_employee_view, name='edit_employee'),
]