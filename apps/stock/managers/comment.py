from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import COMMENT_UD as UD, Post, Comment
from pydantic import UUID4
from fastapi import Body, Request
from fastapi.encoders import jsonable_encoder


class MongoCommentDatabase:
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

    async def get_by_post(self, post_id: str) -> Optional[UD]:
        query = [
            { "$match": { "post._id" : post_id, "parent_id": "" } },
            {
                "$graphLookup": {
                    "from": "comment",
                    "startWith": "$_id",
                    "connectFromField": "_id",
                    "connectToField": "parent_id",
                    "as": "replies"
                }
            }
            ]
        objs = self.collection.aggregate(
            query
        )

        return objs

    async def get_count(self, post_id: str) -> Optional[UD]:
        query = [
            { "$match": {"post._id": post_id} },
            { "$group" : { "_id" : "$post._id", "count" : { "$sum" : 1 } } },
            { "$sort" : { "count" : -1 } }
        ]
        objs = self.collection.aggregate(
            query
        )

        return objs   
        
    async def update_vote(self, id: UUID4, payload: Body = (...)) -> Optional[UD]:
        obj = await self.collection.update_one({"_id": id}, {"$inc" : payload})
        return True


class CommentManager:

    def __init__(self, db_model: Type[UD]):
        self.db_model = db_model
        self.model = Comment
        self.collection = MongoCommentDatabase(Comment, self.db_model)

    async def create(self, obj: UD) -> UD:        
        created_post = await self.collection.create(obj)
        print (created_post)
        return created_post

    
    async def get_comment(self, id: UUID4) -> Optional[UD] :
        post_obj = await self.collection.get(id)
        return post_obj

    async def get_all(self, post_id: str):
        all_comments = []
        comments = await self.collection.get_by_post(post_id)
        async for comment in comments:
            all_comments.append(comment)
        print (all_comments)
        return all_comments

    async def get_count(self, post_id: str):
        comments_list = []
        comments = await self.collection.get_count(post_id)
        async for comment in comments:
            comments_list.append(comment.get('count'))
        return comments_list

    async def update_vote(self, id: UUID4, vote_type: str) -> Optional[UD] :
        payload = {}
        if vote_type == 'up':
            payload = {
                'up_vote': 1,
                'total_votes': 1
            }
        else:
            payload = {
                'down_vote': 1,
                'total_votes': -1
            }
        post_obj = await self.collection.update_vote(id, payload)
        return post_obj



