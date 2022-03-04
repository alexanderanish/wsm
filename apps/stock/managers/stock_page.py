from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import ST_PAGE_UD as UD, StockPage, BEARISH, BULLISH, NEUTRAL
from pydantic import UUID4
from fastapi import Body, Request
from fastapi.encoders import jsonable_encoder
from apps.stock.db.stock_page import MongoStockPageDatabase


class StockPageManager:

    def __init__(self, db_model: Type[UD]):
        self.db_model = db_model
        self.model = StockPage
        self.collection = MongoStockPageDatabase(StockPage, self.db_model)

    async def create(self, obj: UD) -> UD:        
        created_obj = await self.collection.create(obj)
        print (created_obj)
        return created_obj

    async def update(self, id: str, obj: UD) -> UD:
        obj = await self.collection.partial_update(id, obj)
        return obj
    
    async def get(self, id: UUID4) -> Optional[UD] :
        obj = await self.collection.get(id)
        return obj

    async def get_all(self, query_params: Body = (...)):
        query_params = await self.construct_query(query_params)
        objs = await self.collection.get_all(query_params=query_params)
        all_objs = []
        all_objs = await objs.to_list(length=100)
        return all_objs


    async def get_count(self, post_id: str):
        comments_list = []
        comments = await self.collection.get_count(post_id)
        async for comment in comments:
            comments_list.append(comment.get('count'))
        return comments_list

    async def construct_query(self, query_params: Body = (...)):
        query = {}
        name = query_params.get('name')

        if name:
            query['name'] = name
        return query

    async def update_position(self, id: UUID4, position_type: str) -> Optional[UD] :
        payload = {}
        PREFIX = 'position.'
        if position_type == BEARISH:
            payload = {
                PREFIX + BEARISH: 1,
                PREFIX + BULLISH: 0,
                PREFIX + NEUTRAL: 0
            }
        elif position_type == BULLISH:
            payload = {
                PREFIX + BEARISH: 0,
                PREFIX + BULLISH: 1,
                PREFIX + NEUTRAL: 0
            }
        
        elif position_type == NEUTRAL:
            payload = {
                PREFIX + BEARISH: 0,
                PREFIX + BULLISH: 0,
                PREFIX + NEUTRAL: 1
            }
        post_obj = await self.collection.update_position(id, payload)
        return post_obj

    async def get_sentiment(self, stock_id: UUID4) -> Optional[UD]:
        obj = await self.get(stock_id)
        print (obj)
        position = obj.position
        total = sum(position.values())
        out = {}
        for key, val in position.items():
            if val:
                percentage = (val * 100) / total
            else:
                percentage = 0
            out[key] = round(percentage)
        
        return out

    




