from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list_view, name='product_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'), # <--- Nueva ruta
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    # --- Rutas nuevas para pedidos ---
    path('orders/new/', views.procesar_pedido_view, name='new_order'),
    path('myorders/', views.mis_pedidos_view, name='my_orders'),
]