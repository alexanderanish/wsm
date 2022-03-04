
from fastapi import Body, Request, UploadFile
from datetime import datetime
from pydantic import UUID4, EmailStr, ValidationError
from apps.util.utils import apply_pagination
from .models import UserDB
from .utils import save_to_files
from apps.util.utils import generate_otp, safe_open_w
import shutil

class UserUtil:

    def __init__(self, request: Request):
        self.request = request
        self.db_model = request.app.db["users"]
    

    async def update_user(self, email: EmailStr = Body(..., embed=True), payload: Body = (...)):
        user_obj = await self.db_model.update_one(
                    {'email': email}, 
                    payload
                )
        return user_obj
    
    async def update_by_id(self, id: UUID4, payload: Body = (...)):
        user_obj = await self.db_model.update_one(
                    {'id': id}, 
                    payload
                )
        return user_obj
    
    async def get_user(self, email: EmailStr=Body(..., embed=True), payload:Body = (...)):
        return await self.db_model.find_one({'email': email})
    
    async def get_users(self, page_size: int, page_no: int, payload:Body = (...)):
        query = {}
        search_key = payload.get('search_key')
        if search_key:
            query["$text"]= {"$search": search_key}
        cursor = self.db_model.find(query)
        cursor = apply_pagination(cursor, page_no, page_size)
        users = []
        for doc in await cursor.to_list(length=100):
            if doc.get('hashed_password'):
                doc.pop('hashed_password')
            if doc.get('_id'):
                doc.pop('_id')
            users.append(doc)
        return users
    
    def has_already_bookmarked(self, user: UserDB, post_id: UUID4):
        bookmarked = user.get('bookmark_post')
        if bookmarked:
            post_ids = [item.get('post_id') for item in bookmarked]
            return post_id in post_ids
        return False



class UserController(UserUtil):

    def __init__(self, request: Request):
        super(UserController, self).__init__(request)

    async def join_st_page(self, email: EmailStr, params: Body = (...)):
        try:
            user_obj = await self.get_user(email)
            stock_name = params.get('stock_name')
            stock_id = params.get('stock_id')
            created_time = datetime.now()
            if user_obj:
                try:
                    payload = {
                        "$push": {'st_page_subscribed': {'name': stock_name, '_id': stock_id, 'joined_time': created_time}}
                    }
                    await self.update_user(email, payload)
                except Exception as e:
                    raise ValueError(str(e))
            else:
                return False
        except Exception:
                raise ValueError('Error While updating StockPage Subscription details on User')

            
    async def update_st_position(self, email: EmailStr=Body(..., embed=True), params: Body = (...)):
        try:
            user_obj = await self.get_user(email)
            if user_obj:
                stock_id = params.get('stock_id')
                position_type = params.get('position_type')
                created_time = datetime.now()
                try:
                    payload = {
                        "$push": {'st_page_positioned': {
                            'st_id': stock_id, 
                            'positioned_time': datetime.now(),
                            'position': position_type}}
                    }
                    await self.update_user(email, payload)
                except Exception as e:
                    raise ValueError(str(e))
            else:
                raise ValueError('User Doesnot exist in the system')
        except Exception as e:
                raise ValueError(str(e))
    
    
    async def bookmark_post(self, email: EmailStr=Body(..., embed=True), params: Body = (...)):
        try:
            user_obj = await self.get_user(email)
            post_id = params.get('post_id')
            if user_obj:
                if self.has_already_bookmarked(user_obj, post_id):
                    raise ValueError('User has already bookmarked this post.')
                created_time = datetime.now()
                try:
                    payload = {
                        "$push": {'bookmark_post': {
                            'post_id': post_id, 
                            'created_at': datetime.now()
                        }}
                    }
                    await self.update_user(email, payload)
                except Exception as e:
                    raise ValueError(str(e))
            else:
                raise ValueError('User Doesnot exist in the system')
        except Exception as e:
                raise ValueError(str(e))
    
    async def un_bookmark_post(self, email: EmailStr=Body(..., embed=True), params: Body = (...)):
        try:
            user_obj = await self.get_user(email)
            post_id = params.get('post_id')
            if user_obj:
                created_time = datetime.now()
                try:
                    payload = {
                        "$pull": {'bookmark_post': {
                            'post_id': post_id
                        }}
                    }
                    await self.update_user(email, payload)
                except Exception as e:
                    raise ValueError(str(e))
            else:
                raise ValueError('User Doesnot exist in the system')
        except Exception as e:
                raise ValueError(str(e))
    
    async def update_profile_pic(self, id: UUID4, profile_picture: UploadFile):
        try:

            user = await self.request.app.fastapi_users.db.get(id)
            if user:
                upload_path = 'static/profile-pic/' + profile_picture.filename
                try:
                    payload = {
                        "$set": {'profile_picture': upload_path}
                    }
                    await self.update_by_id(id, payload)
                    await save_to_files(profile_picture, 'profile-pic')
                except Exception as e:
                    raise ValueError(str(e))
            else:
                raise ValueError('User Doesnot exist in the system')
        except Exception as e:
                raise ValueError(str(e))