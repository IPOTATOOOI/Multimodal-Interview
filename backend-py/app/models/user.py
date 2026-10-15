from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    hashed_password: str
    created_at: datetime

    class Config:
        orm_mode = True