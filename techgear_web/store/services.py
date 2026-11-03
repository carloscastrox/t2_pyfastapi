import requests

API_URL = "http://127.0.0.1:8000"

def get_products():
    """Obtiene el catálogo de productos desde FastAPI"""
    try:
        response = requests.get(f"{API_URL}/products")
        return response.json() if response.status_code == 200 else []
    except requests.exceptions.RequestException:
        return []
    
def register_user(user_data):
    """Registra un nuevo usuario con rol de cliente fijo en FastAPI"""
    try:
        payload = {
            "username": user_data["username"],
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "role": "cliente",  # <--- Forzado estrictamente a cliente
            "password": user_data["password"]
        }
        response = requests.post(f"{API_URL}/users", json=payload)
        return response.status_code == 201
    except requests.exceptions.RequestException:
        return False
    
def authenticate_user(username, password):
    """Autentica al usuario en FastAPI y retorna el token JWT"""
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except requests.exceptions.RequestException:
        return None

def create_product(product_data, token):
    """Crea un producto (Requiere rol de administrador en FastAPI)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/products", json=product_data, headers=headers)
    return response.status_code == 201