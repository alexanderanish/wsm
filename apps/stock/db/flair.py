from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import FLAIR_UD as UD, Flair
from pydantic import UUID4
from fastapi import Body, Request
from fastapi.encoders import jsonable_encoder


class MongoFlairDatabase:
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

    async def get_by_name(self, name: str) -> Optional[UD]:
        user = await self.collection.find_one(
            {"name": name}
        )
        return self.db_model(**user) if user else None

    async def create(self, obj: UD) -> UD:
        obj = jsonable_encoder(obj)
        await self.collection.insert_one(obj)
        return obj

    async def update(self, obj: UD) -> UD:
        await self.collection.replace_one({"_id": id}, obj.dict())
        return obj

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})

    async def partial_update(self, id: str, obj: UD) -> UD:
        await self.collection.update_one({"_id": id}, {"$set" : obj.dict()})
        return obj