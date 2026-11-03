from pydantic import BaseModel, Field
from typing import List, Literal

class OrderItem(BaseModel):
    product_id: str = Field(..., description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad comprada")

class OrderSchema(BaseModel):
    user_id: str = Field(..., description="ID del cliente que realiza el pedido")
    items: List[OrderItem] = Field(..., description="Lista de productos del pedido")
    total_price: float = Field(..., ge=0, description="Costo total de la orden")
    status: Literal["pendiente", "procesando", "enviado", "entregado", "cancelado"] = Field("pendiente")