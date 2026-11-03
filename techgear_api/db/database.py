import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Cargar variables de entorno (busca el archivo .env)
load_dotenv()

# Obtener la URL de conexión
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Conectar al cluster de MongoDB
client = AsyncIOMotorClient(MONGO_URL)

# Crear o acceder a la base de datos
database = client.techgear_db