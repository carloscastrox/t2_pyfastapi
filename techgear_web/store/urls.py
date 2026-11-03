from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'), # <--- Nueva ruta
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]