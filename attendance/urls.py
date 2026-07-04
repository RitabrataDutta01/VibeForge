from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path("", views.attendance_home, name="home"),
    path("admin-view/", views.attendance_admin_roster, name="admin_roster"),
]