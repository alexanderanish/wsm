from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import ST_PAGE_UD as UD, StockPage
from pydantic import UUID4
from fastapi import Body, Request
from fastapi.encoders import jsonable_encoder


class MongoStockPageDatabase:
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
        objs = self.collection.find(query_params)
        return objs

    async def get_by_author(self, email: str) -> Optional[UD]:
        user = await self.collection.find_one(
            {"author": email}
        )
        return self.db_model(**user) if user else None

    
    async def create(self, obj: UD) -> UD:
        obj = jsonable_encoder(obj)
        await self.collection.insert_one(obj)
        return obj

    async def update(self, obj: UD) -> UD:
        print ('77777777')
        print (obj)
        # print (obj._id)
        await self.collection.replace_one({"_id": id}, obj.dict())
        print ('#######################')
        return obj

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})

    async def partial_update(self, id: str, obj: UD) -> UD:
        print (id)
        print ('>>>>')
        print (obj.dict())

        await self.collection.update_one({"_id": id}, {"$set" : obj.dict()})
        return obj

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

    async def update_position(self, id: UUID4, payload: Body = (...)) -> Optional[UD]:
        obj = await self.collection.update_one({"_id": id}, {"$inc" : payload})
        return True