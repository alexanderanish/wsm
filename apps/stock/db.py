from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from .models import UD
from pydantic import UUID4
from fastapi import Body, Request
from .models import Post
from fastapi.encoders import jsonable_encoder


class MongoPostDatabase:
    """
    Database adapter for MongoDB.

    :param user_db_model: Pydantic model of a DB representation of a user.
    :param collection: Collection instance from `motor`.
    """
    collection: AsyncIOMotorCollection

    def __init__(
        self,
        db_model: Type[UD],
        collection: AsyncIOMotorCollection
    ):
        # super().__init__(db_model)
        self.db_model = db_model
        self.collection = collection

    async def get(self, id: UUID4) -> Optional[UD]:
        obj = await self.collection.find_one({"_id": id})
        return self.db_model(**obj) if obj else None

    async def get_all(self, query_params: Body = (...)) -> Optional[UD]:
        obj = await self.collection.find(query_params)
        return self.db_model(**obj) if obj else None

    async def get_by_author(self, email: str) -> Optional[UD]:
        user = await self.collection.find_one(
            {"author": email}
        )
        return self.db_model(**user) if user else None

    async def create(self, obj: UD) -> UD:
        obj = jsonable_encoder(obj)
        await self.collection.insert_one(obj)
        return obj

    async def update(self, user: UD) -> UD:
        await self.collection.replace_one({"id": user.id}, user.dict())
        return user

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})

    async def partial_update(self, obj: UD) -> UD:
        await self.collection.update_one({"_id": obj.id}, obj.dict())
        return user


class PostManager:

    def __init__(self, request: Request):
        self.db_model = request.app.db["post"]
        self.model = Post
        self.post_collection = MongoPostDatabase(Post, self.db_model)

    async def create_post(self, obj: UD) -> UD:        
        created_post = await self.post_collection.create(obj)
        print (created_post)
        return created_post

    async def get_all_posts(self, query_params: Body = (...)):
        st_page = query_params.get('st_page')
        if st_page:
            query_params["stock_page._id"] = st_page

        for doc in await self.post_collection.get_all(query_params=query_params).to_list(length=100):
            posts.append(doc)
        return posts

    async def get_post(self, id: UUID4) -> Optional[UD] :
        post_obj = await self.post_collection.get(id)
        return post_obj



