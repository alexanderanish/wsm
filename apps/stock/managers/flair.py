from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import FLAIR_UD as UD, Flair
from pydantic import UUID4
from fastapi import Body, Request
from fastapi.encoders import jsonable_encoder
from apps.stock.db.flair import MongoFlairDatabase


class FlairManager:

    def __init__(self, db_model: Type[UD]):
        self.db_model = db_model
        self.model = Flair
        self.collection = MongoFlairDatabase(Flair, self.db_model)

    async def create(self, obj: UD, user=None) -> UD:  
        if await self.get_by_name(obj.name):
            raise ValueError("Flair already exist.")
        created_obj = await self.collection.create(obj)
        print (created_obj)
        return created_obj

    async def update(self, id: str, obj: UD) -> UD:
        obj = await self.collection.partial_update(id, obj)
        return obj
    
    async def get(self, id: UUID4) -> Optional[UD] :
        obj = await self.collection.get(id)
        return obj
    
    async def get_by_name(self, name: str) -> Optional[UD] :
        obj = await self.collection.get_by_name(name)
        return obj

    async def get_all(self, query_params: Body = (...)):
        query_params = await self.construct_query(query_params)
        objs = await self.collection.get_all(query_params=query_params)
        all_objs = []
        all_objs = await objs.to_list(length=100)
        return all_objs
        


    async def construct_query(self, query_params: Body = (...)):
        query = {}
        name = query_params.get('name')

        if name:
            query['name'] = name
        return query