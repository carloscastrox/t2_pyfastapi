from django.shortcuts import render, redirect
from django.contrib import messages
from .services import get_products, authenticate_user, create_product, register_user
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

def login_view(request):
    """Vista de inicio de sesión para almacenar el JWT en la sesión de Django"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            token = authenticate_user(username, password)
            if token:
                request.session['access_token'] = token
                request.session['username'] = username
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