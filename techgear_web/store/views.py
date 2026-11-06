
import base64
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from .services import get_products, authenticate_user, create_product, register_user, get_user_orders, create_order
from .forms import LoginForm, ProductForm, RegisterForm


def product_list_view(request):
    """Vista principal: Muestra el catálogo de productos"""
    products = get_products()
    return render(request, 'product_list.html', {'products': products})

def register_view(request):
    """Vista de registro para nuevos clientes"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            success = register_user(form.cleaned_data)
            if success:
                messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
                return redirect('login')
            else:
                messages.error(request, "Error al registrarse. El usuario o correo ya podría existir.")
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

import base64
import json

def decode_jwt_payload(token):
    """Decodifica el payload de un token JWT sin necesidad de librerías externas"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        payload_enc = parts[1]
        padded = payload_enc + '=' * (-len(payload_enc) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        return json.loads(decoded_bytes.decode('utf-8'))
    except Exception:
        return {}

def login_view(request):
    """Vista de inicio de sesión para almacenar el JWT y el rol en la sesión de Django"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            token = authenticate_user(username, password)
            if token:
                request.session['access_token'] = token
                request.session['username'] = username
                
                # Extraer y guardar el rol del usuario desde el token JWT
                payload = decode_jwt_payload(token)
                request.session['role'] = payload.get('role', 'cliente')
                
                messages.success(request, "¡Bienvenido a TechGear!")
                return redirect('product_list')
            else:
                messages.error(request, "Credenciales inválidas")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    """Cierra sesión limpiando el token"""
    request.session.flush()
    return redirect('product_list')

def admin_dashboard_view(request):
    """Panel de administración para registrar productos"""
    token = request.session.get('access_token')
    if not token:
        messages.warning(request, "Debes iniciar sesión para acceder.")
        return redirect('login')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            success = create_product(form.cleaned_data, token)
            if success:
                messages.success(request, "Producto creado exitosamente en la API.")
                return redirect('product_list')
            else:
                messages.error(request, "Error al crear el producto (Verifica permisos de administrador).")
    else:
        form = ProductForm()
    
    return render(request, 'admin_dashboard.html', {'form': form})


# Pedidos del cliente

def mis_pedidos_view(request):
    token = request.session.get("access_token")
    if not token:
        return redirect("login")
    
    orders = get_user_orders(token)
    
    # Calcular el total de unidades en Django por seguridad
    for order in orders:
        items = order.get("items", [])
        total_qty = sum(item.get("quantity", 1) for item in items)
        order["total_quantity"] = total_qty
        
    return render(request, "my_orders.html", {"orders": orders})

def procesar_pedido_view(request):
    token = request.session.get("access_token")
    if not token:
        return redirect("login")
    
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        
        # Estructura requerida por OrderItem
        items_data = [
            {
                "product_id": product_id,
                "quantity": quantity
            }
        ]
        
        success = create_order(items_data, token)
        if success:
            return redirect("my_orders")
            
    return redirect("product_list")