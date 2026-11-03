from pydantic import BaseModel, Field
from typing import Optional

class ProductSchema(BaseModel):
    name: str = Field(..., description="Nombre del producto de hardware")
    description: str = Field(..., description="Descripción detallada del componente")
    price: float = Field(..., gt=0, description="Precio del producto")
    stock: int = Field(..., ge=0, description="Cantidad disponible en inventario")
    category: str = Field(..., description="Categoría (ej. Procesadores, Tarjetas Gráficas)")
    image_url: Optional[str] = Field(None, description="URL de la imagen del producto")

class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    image_url: Optional[str] = None