from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str
    role: Literal["cliente", "administrador"] = Field("cliente", description="Rol del usuario en la plataforma")
    password: str = Field(..., min_length=6, description="Contraseña de usuario")

class UserLoginSchema(BaseModel):
    username: str
    password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str