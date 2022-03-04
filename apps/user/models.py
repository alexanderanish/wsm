from typing import Optional
import uuid
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from datetime import datetime
from fastapi import Body


class UserBase(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = True
    last_login: Optional[datetime] = Body(None)
    date_joined: Optional[datetime] = Body(None)


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "username": "john",
                "email": "jdoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True,
                "is_superuser": True
            }
        }

class UserIn(UserBase):
    password: Optional[str] = None


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


class UpdateUserModel(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "firstname": "John",
                "lastname": "Doe"
            }
        }


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db