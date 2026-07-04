from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', login_required(RedirectView.as_view(pattern_name='profile', permanent=False)), name='home'),
    path('create-employee/', views.signup_view, name='create_employee'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('employees/', views.employee_list_view, name='employee_list'),
    path('employees/<int:profile_id>/edit/', views.edit_employee_view, name='edit_employee'),
]