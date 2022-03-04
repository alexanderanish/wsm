from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, FilePath
import uuid
import datetime
from apps.stock.models import BaseStockPage

class User(BaseUser):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    has_verified: bool = False
    st_page_subscribed: Optional[List[BaseStockPage]] = []
    st_page_positioned: Optional[List[dict]] = []
    bookmark_post: Optional[List[dict]] = []
    date_joined: datetime.datetime = datetime.datetime.now() 


class UserCreate(BaseUserCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    has_verified: bool = False
    st_page_subscribed: Optional[List[BaseStockPage]] = []
    st_page_positioned: Optional[List[dict]] = []
    bookmark_post: Optional[List[dict]] = []
    date_joined: datetime.datetime = datetime.datetime.now() 


class UserUpdate(BaseUserUpdate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    has_verified: Optional[bool] = False
    st_page_subscribed: Optional[List[BaseStockPage]] = []
    st_page_positioned: Optional[List[dict]] = []
    bookmark_post: Optional[List[dict]] = []
    profile_picture: Optional[FilePath] = None

class UserAdditionalUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # profile_picture: Optional[FilePath] = None


class UserDB(User, BaseUserDB):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    has_verified: Optional[bool] = False
    st_page_subscribed: Optional[List[BaseStockPage]] = []
    st_page_positioned: Optional[List[dict]] = []
    bookmark_post: Optional[List[dict]] = []
    date_joined: datetime.datetime = datetime.datetime.now() 


class UserView(BaseUser):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    has_verified: Optional[bool] = False
    date_joined: datetime.datetime = datetime.datetime.now() 


class UserOTP(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    email: EmailStr
    otp: str = Field(...)
    date_created: datetime.datetime = datetime.datetime.now()
    validity:int = 10

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    
class UserAnalytics(BaseModel):
    pass
