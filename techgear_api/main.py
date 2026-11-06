from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId

from db.database import database
from models.product_model import ProductSchema, ProductUpdateSchema
from models.users_model import UserSchema, TokenSchema
from models.orders_model import OrderItem, OrderSchema

# --- CONFIGURACIÓN DE SEGURIDAD Y JWT ---
SECRET_KEY = "tu_clave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def order_helper(order) -> dict:
    total_quantity = sum(item.get("quantity", 1) for item in order.get("items", []))
    return {
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "items": order["items"],
        "total_quantity": total_quantity,  # <--- Esta línea es la que alimenta la vista
        "total_price": order["total_price"],
        "status": order["status"]
    }
    
# --- UTILIDADES DE CONTRASEÑAS Y TOKENS (DEFINIDAS PRIMERO) ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- CICLO DE VIDA (LIFESPAN) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear usuario administrador por defecto si no existe
    admin_exists = await database.users.find_one({"role": "administrador"})
    if not admin_exists:
        hashed_password = get_password_hash("admin123")
        default_admin = {
            "username": "admin",
            "email": "admin@techgear.com",
            "full_name": "Administrador TechGear",
            "role": "administrador",
            "password": hashed_password
        }
        await database.users.insert_one(default_admin)
        print("Usuario Administrador predeterminado creado (Usuario: admin | Contraseña: admin123)")
    
    yield

app = FastAPI(
    title="TechGear API",
    description="API RESTful con autenticación JWT para el sistema híbrido TechGear",
    version="1.2.0",
    lifespan=lifespan
)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await database.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user_helper(user)

# --- HELPERS DE SERIALIZACIÓN ---
def product_helper(product) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "description": product["description"],
        "price": product["price"],
        "stock": product["stock"],
        "category": product["category"],
        "image_url": product.get("image_url")
    }

def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"]
    }

def order_helper(order) -> dict:
    return {
        "id": str(order["_id"]),
        "user_id": order["user_id"],
        "items": order["items"],
        "total_price": order["total_price"],
        "status": order["status"]
    }

# --- ENDPOINT DE AUTENTICACIÓN (LOGIN) ---
@app.post("/token", response_model=TokenSchema, tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await database.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- ENDPOINTS DE USUARIOS ---
@app.post("/users", response_description="Registrar usuario", status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
async def create_user(user: UserSchema):
    user_dict = user.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])
    new_user = await database.users.insert_one(user_dict)
    created_user = await database.users.find_one({"_id": new_user.inserted_id})
    return user_helper(created_user)

@app.get("/users", response_description="Listar usuarios", response_model=List[dict], tags=["Usuarios"])
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "administrador":
        raise HTTPException(status_code=403, detail="Acceso no autorizado")
    users = []
    async for user in database.users.find():
        users.append(user_helper(user))
    return users


# --- ENDPOINTS DE PRODUCTOS ---
@app.get("/products", response_description="Listar todos los productos", response_model=List[dict], tags=["Productos"])
async def get_products():
    products = []
    async for product in database.products.find():
        products.append(product_helper(product))
    return products

@app.post("/products", response_description="Crear un nuevo producto", status_code=status.HTTP_201_CREATED, tags=["Productos"])
async def create_product(product: ProductSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "administrador":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    product_dict = product.model_dump()
    new_product = await database.products.insert_one(product_dict)
    created_product = await database.products.find_one({"_id": new_product.inserted_id})
    return product_helper(created_product)

@app.get("/products/{id}", response_description="Obtener producto por ID", tags=["Productos"])
async def get_product(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    product = await database.products.find_one({"_id": ObjectId(id)})
    if product:
        return product_helper(product)
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.put("/products/{id}", response_description="Actualizar producto", tags=["Productos"])
async def update_product(id: str, product: ProductUpdateSchema, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "administrador":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    
    update_data = {k: v for k, v in product.model_dump().items() if v is not None}
    if len(update_data) >= 1:
        update_result = await database.products.update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if update_result.modified_count == 1:
            updated_product = await database.products.find_one({"_id": ObjectId(id)})
            return product_helper(updated_product)
    
    existing_product = await database.products.find_one({"_id": ObjectId(id)})
    if existing_product:
        return product_helper(existing_product)
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@app.delete("/products/{id}", response_description="Eliminar producto", tags=["Productos"])
async def delete_product(id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "administrador":
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    delete_result = await database.products.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return {"message": "Producto eliminado exitosamente"}
    raise HTTPException(status_code=404, detail="Producto no encontrado")


# --- ENDPOINTS DE PEDIDOS ACTUALIZADOS ---
@app.post("/orders", response_description="Crear un pedido", status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
async def create_order(items: List[OrderItem], current_user: dict = Depends(get_current_user)):
    total_price = 0.0
    validated_items = []
    
    for item in items:
        if not ObjectId.is_valid(item.product_id):
            raise HTTPException(status_code=400, detail="ID de producto inválido")
        
        product = await database.products.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        
        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product['name']}")
        
        # Descontar stock automáticamente
        await database.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )
        
        total_price += product["price"] * item.quantity
        validated_items.append({"product_id": item.product_id, "quantity": item.quantity})

    order_dict = {
        "user_id": current_user["id"],  # Asociado automáticamente al usuario logueado
        "items": validated_items,
        "total_price": total_price,
        "status": "pendiente"
    }
    
    new_order = await database.orders.insert_one(order_dict)
    created_order = await database.orders.find_one({"_id": new_order.inserted_id})
    return order_helper(created_order)

@app.get("/orders", response_description="Listar pedidos", response_model=List[dict], tags=["Pedidos"])
async def get_orders(current_user: dict = Depends(get_current_user)):
    # Si es administrador ve todos; si es cliente, solo sus propios pedidos
    query = {} if current_user["role"] == "administrador" else {"user_id": current_user["id"]}
    
    orders = []
    async for order in database.orders.find(query):
        orders.append(order_helper(order))
    return orders