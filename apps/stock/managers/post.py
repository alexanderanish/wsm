from typing import Optional, Type

from motor.motor_asyncio import AsyncIOMotorCollection
from apps.stock.models import UD, Post
from pydantic import UUID4
from fastapi import Body, Request, UploadFile
from fastapi.encoders import jsonable_encoder
from datetime import datetime


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

    async def get_all(self, query_params: Body = (...), sort_by=None, limit=None) -> Optional[UD]:
        objs = self.collection.find(query_params)
        if sort_by:
            objs = objs.sort(sort_by[0], sort_by[1])
        if limit:
            objs = objs.limit(limit)
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

    async def update(self, id:UUID4, obj: UD) -> UD:
        print ('>>>>>>>>>')
        print (obj.dict())
        await self.collection.update_one({"_id": -1}, {"$set" : obj.dict()})
        return obj

    async def delete(self, user: UD) -> None:
        await self.collection.delete_one({"id": user.id})

    async def partial_update(self, id: UUID4, payload: Body = (...)) -> Optional[UD]:
        await self.collection.update_one({"_id": obj.id}, {"$set" : payload})
        return True
    
    async def update_vote(self, id: UUID4, payload: Body = (...)) -> Optional[UD]:
        obj = await self.collection.update_one({"_id": id}, {"$inc" : payload})
        return True
    
    async def get_user_thrust_point(self, payload: Body = (...)) -> Optional[UD]:

        """
        db.post.aggregate([
            {
                $match: {
                "author": "fahim1@example.com"
                }
            },
            {
                "$unionWith": {
                "coll": "comment",
                pipeline: [
                    {
                    $match: {
                        "author": "fahim1@example.com"
                    }
                    }
                ]
                }
            },
            {
                $group: {
                _id: "$author",
                total_votes: {
                    $sum: "$total_votes"
                }
                }
            }
            ])

        """
        author = payload.get('author')
        match_query = {}
        if author:
            match_query["author"] = author
        # query = [
        #     { "$match": match_query },
        #     { "$group" : { "_id" : "$author", "count" : { "$sum" : "$total_votes" } } },
        #     { "$sort" : { "count" : -1 } }
        # ]

        query = [
            { "$match": match_query },
            {
                "$unionWith": {
                    "coll": "comment",
                    "pipeline": [
                        {
                            "$match": match_query
                        }
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$author",
                    "total_votes": {
                        "$sum": "$total_votes"
                    }
                }
            },
            { "$sort" : { "total_votes" : -1 } }
        ]


        print (query)
        objs = self.collection.aggregate(
            query
        )
        print (objs)
        return objs


class PostManager:

    RECENT_RECORD_LIMIT = 10

    def __init__(self, db_model: Type[UD]):
        self.db_model = db_model
        self.model = Post
        self.collection = MongoPostDatabase(Post, self.db_model)

    async def create_post(self, obj: UD, upload_image: UploadFile) -> UD:        
        await self.check_validation_error(obj)
        created_post = await self.collection.create(obj)
        if obj.image:
            await self.update_media(created_post.id, upload_image)
        return created_post

    async def update(self, id: str, obj: UD) -> UD:
        obj = await self.collection.update(id, obj)
        return obj

    async def get_all(self, params: Body = (...)):
        query_params = self.construct_query(params)
        sort_by, limit = self.get_sort_info(params)
        posts = await self.collection.get_all(query_params=query_params, sort_by=sort_by, limit=limit)
        print (posts)
        all_posts = []
        all_posts = await posts.to_list(length=100)
        return all_posts


    def get_sort_info(self, params):
        sort_info = ('created_utc', -1)
        filter_by = params.get('filter_by')
        if filter_by == 'recent':
            return sort_info, self.RECENT_RECORD_LIMIT
        
        sort_by = params.get('sort_by')

        if sort_by == 'recent':
            sort_info = ('created_utc', -1)
        elif sort_by == 'old':
            sort_info = ('created_utc', 1)                 
        elif sort_by == 'high-thrust':
            sort_info = ('total_votes', -1)
        elif sort_by == 'low-thrust':
            sort_info = ('total_votes', 1)
        
        return sort_info, None

    def construct_query(self, query_params: Body = (...)):
        mongo_query_params = {}
        st_page = query_params.get('st_page')
        if st_page:
            mongo_query_params["stock_page._id"] = st_page
        
        author = query_params.get("author")
        if author:
            mongo_query_params["author"] = author
        
        from_date = query_params.get("from_date")
        to_date = query_params.get("to_date")
        # if from_date:
        #     from_date = datetime.strptime(from_date, "%d/%m/%Y")
        # if to_date:
        #     to_date = datetime.strptime(to_date, "%d/%m/%Y")
        if from_date and to_date:
            mongo_query_params["created_utc"] = {
                "$gte": from_date,
                "$lt": to_date,
            }
        
        min_thrust = query_params.get("min_thrust")
        max_thrust = query_params.get("max_thrust")
        if min_thrust and max_thrust:
            mongo_query_params["total_votes"] = {
                "$gte": int(min_thrust),
                "$lte": int(max_thrust),
            }
        elif min_thrust:
            mongo_query_params["total_votes"] = {"$gte": int(min_thrust)}
        elif max_thrust:
            mongo_query_params["total_votes"] = {"$gte": int(max_thrust)}
        
        flair = query_params.get("flair")
        if flair:
            mongo_query_params["flairs.name"] = flair
        
        keyword = query_params.get('keyword')
        if keyword:
            mongo_query_params["$text"] = {"$search": keyword}

        show_draft = query_params.get("show_draft")
        
        if show_draft == 'true':
            mongo_query_params['has_draft'] = True
        else:
            mongo_query_params['has_draft'] = {"$ne":True}
        
        
        print ('###########')
        print (mongo_query_params)
        
        return mongo_query_params
    
    async def check_validation_error(self, obj: UD) -> UD :
        # flairs = obj.flairs
        # if flairs
        #     print (flairs)
        #     raise ValueError("Falirs not exist.")
        return False

    async def get_post(self, id: UUID4) -> Optional[UD] :
        post_obj = await self.collection.get(id)
        return post_obj

    async def partial_update(self, id: UUID4, payload: Body = (...)) -> Optional[UD] :
        post_obj = await self.collection.partial_update(id, payload)
        return post_obj

    async def update_comment(self, id: UUID4, has_add=True) -> Optional[UD] :
        post_obj = await self.collection.get(id)
        if post_obj:
            num_comments = 0
            if has_add:
                num_comments = post_obj.num_comments + 1
            else:
                num_comments = post_obj.num_comments - 1
            payload = {'num_comments': post_obj.num_comments + 1}
            status = await self.collection.partial_update(id, payload)
            return post_obj
        return None


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

    async def get_user_thrust_point(self, author: Optional[str] = None):
        paylaod = {}
        if author:
            paylaod['author'] = author
        out = await self.collection.get_user_thrust_point(paylaod)
        thrust_points = []
        async for item in out:
            thrust_points.append(item)
        return thrust_points
    
    async def update_media(self, id: UUID4, media_file: UploadFile):
        try:
            if id:
                upload_path = 'static/post/images/' + media_file.filename
                try:
                    payload = {
                        "$set": {'image': upload_path}
                    }
                    await self.update_by_id(id, payload)
                    await save_to_files(profile_picture, 'profile-pic')
                except Exception as e:
                    raise ValueError(str(e))
            else:
                raise ValueError('User Doesnot exist in the system')
        except Exception as e:
                raise ValueError(str(e))




