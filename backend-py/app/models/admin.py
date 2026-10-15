from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdminCreate(BaseModel):
    username: str
    password: str
    email: str

class AdminLogin(BaseModel):
    username: str
    password: str


class AdminCreateUser(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class AdminResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    status: int