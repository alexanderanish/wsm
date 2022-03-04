from fastapi_users.models import BaseUser, BaseUserCreate, BaseUserUpdate, BaseUserDB
from typing import Optional, List, TypeVar
from pydantic import BaseModel, Field, EmailStr, ValidationError, validator
import uuid
import datetime
import json

BEARISH = 'bearish'
BULLISH = 'bullish'
NEUTRAL = 'neutral'


class BaseStockPage(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")

class StockPage(BaseStockPage):
    name: str = Field(...)
    spoilers_enabled: Optional[bool] = False
    created_utc: datetime.datetime = datetime.datetime.now()
    description: Optional[str] = None
    display_name: Optional[str] = None
    public_description: Optional[str] = None
    subscribers: Optional[int] = 0
    position: dict = {
        BEARISH: 0,
        BULLISH: 0,
        NEUTRAL: 0
    }

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "Tesla",
                "description": "Stock Description",
                "display_name": "Tesla Inc",
                "public_description": "Tesla Inc",
                "spoilers_enabled": False,
            }
        }

class StockPageUpdate(BaseModel):
    name: str = Field(...)
    spoilers_enabled: Optional[bool] = False
    description: Optional[str] = None
    display_name: Optional[str] = None
    public_description: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "Tesla",
                "description": "Stock Description",
                "display_name": "Tesla Inc",
                "public_description": "Tesla Inc",
                "spoilers_enabled": False,
            }
        }

    
class BasePost(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")


class Post(BasePost):
    """
    author
	comments
	created_utc
	distinguished
	edited
	id
	is_original_content
	link_flair_template_id
	link_flair_text
	locked
	name
	num_comments
	permalink
	poll_data
	saved
	score
	selftext
	spoiler
	stickied
	StockPage : List[1, 2, 3]
	title
	upvote_ratio
	url
	Up_vote_count
	Down_Vote_count
	Total Vote_count
	Net-Vote
    """

    name: str = Field(...)
    title: str = Field(...)
    author: str = Field(...)
    comments: List[str] = []
    spoilers_enabled: Optional[bool] = False
    created_utc: datetime.datetime = datetime.datetime.now()
    distinguished: Optional[bool] = False
    stock_page: Optional[List[BaseStockPage]] = None
    has_edited: Optional[bool] = False
    is_original_content: Optional[bool] = True
    has_locked: Optional[bool] = False
    has_saved: Optional[bool] = True
    has_stickied: Optional[bool] = False
    num_comments: Optional[int] = 0
    up_vote: Optional[int] = 0
    down_vote: Optional[int] = 0
    total_votes: Optional[int] = 0
    # poll_data: Optional[List[]] = []
    url: Optional[str] = ""
    selftext: Optional[str] = ""
    has_draft: Optional[bool] = False
    flairs: Optional[List[dict]] = []
    image: Optional[str] = None
    link: Optional[str] = None

    @validator('author')
    def author_exist(cls, v):
        if not v:
            raise ValueError('Author Doesnot Empty')
        return v
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_to_json

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "name": "I will be interviewing for the Associate Analyst position.",
                "title": "Interviewing for Associate Analyst, any tips I should know going into it?",
                "stock_page": [{"_id": "8a3553a4-0952-43e3-a8d5-cd7ae3075f2c"}],
                "author": "azarmhmd21@gmail.com",
                "has_draft": False,
                "flairs": [{"name": "Name of flair1"}, {"name": "Name of flair2"}],
                'link': ""
                
            }
        }





class Comment(BaseModel):
    """
    author
	comments
	created_utc
	distinguished
	edited
	id
	
    """
    
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    title: Optional[str] = Field(...)
    author: str = Field(...)
    description: Optional[str] = Field(...)
    spoilers_enabled: Optional[bool] = False
    created_utc: datetime.datetime = datetime.datetime.now()
    distinguished: Optional[bool] = False
    post: Optional[BasePost] = None
    up_vote: Optional[int] = 0
    down_vote: Optional[int] = 0
    total_votes: Optional[int] = 0
    parent_id: Optional[str] = Field(...) 

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "Comment title",
                "description": "Any Describtion on the Comment/Reply",
                "post": {'_id': "post_id"},
                "author": "azarmhmd21@gmail.com",
                "parent_id": "If it is a Reply, ID of Parent Comment"
                
            }
        }





class Subscription(BaseModel):
    """
    id
    created_utc
    stockPage
    user
	
    """
    
    id: str = Field(default_factory=uuid.uuid4, alias="_id")


class UpdatePost(BaseModel):

    name: str = Field(...)
    title: str = Field(...)
    spoilers_enabled: Optional[bool] = False
    distinguished: Optional[bool] = False
    has_edited: Optional[bool] = False
    is_original_content: Optional[bool] = True
    has_locked: Optional[bool] = False
    has_saved: Optional[bool] = True
    has_stickied: Optional[bool] = False
    # poll_data: Optional[List[]] = []
    url: Optional[str] = ""
    selftext: Optional[str] = ""
    has_draft: Optional[bool] = False
    flairs: Optional[List[dict]] = []
    image: Optional[str] = None
    link: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Title of the Post",
                "name": "Name of the post",
                "spoilers_enabled": False,
                "distinguished": False,
                "has_edited": False,
                "spoilers_enabled": False,
                "is_original_content": True,
                "has_locked": False,
                "has_stickied": False,
                "has_saved": True,
                "url": "https://<>",
                "selftext": "Self Text of the post",
                "has_draft": False,
                "flairs": [{"name": "Name of flair1"}, {"name": "Name of flair2"}]
            }
        }

class Flair(BaseModel):
    """
    id
    name
    description
    created_by
	created_at
    """
    
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    name: str = Field(...)
    description: Optional[str] = Field(...)
    created_by: str = Field(...)
    created_at: datetime.datetime = datetime.datetime.now()
    is_active: Optional[bool] = True

    class Config:
        schema_extra = {
            "example": {
                "name": "Name of the Flair",
                "description": "Description of the flair",
                "is_active": True,
                "created_by": "user@example.com"
                
            }
        }
    


UD = TypeVar("UD", bound=Post)
COMMENT_UD = TypeVar("COMMENT_UD", bound=Comment)
ST_PAGE_UD = TypeVar("ST_PAGE_UD", bound=StockPage)
FLAIR_UD = TypeVar("FLAIR_UD", bound=Flair)