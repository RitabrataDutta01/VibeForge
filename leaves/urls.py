from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path("", views.leave_home, name="home"),
    path("admin-view/", views.leave_admin_list, name="admin_list"),
    path("<int:leave_id>/<str:decision>/", views.leave_decide, name="decide"),
]