from fastapi import APIRouter, Body, Request, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .models import StockPage, Post, Comment, StockPageUpdate, UpdatePost, Flair
from typing import Callable, Optional, Type
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from datetime import datetime
import asyncio
from pydantic import UUID4, EmailStr, ValidationError
from .common import StockController
from apps.auth.common import UserController
from apps.auth.models import UserDB

router = APIRouter()


def stock_page_router(app):

    router = APIRouter()

    @router.post("/create-stock-page", response_description="Add new Stock Page",)
    async def create_stock_page(request: Request, stock_page: StockPage = Body(...)):
        # stock_page = jsonable_encoder(stock_page)
        # new_task = await request.app.db["stockPage"].insert_one(stock_page)
        # created_task = await request.app.db["stockPage"].find_one(
        #     {"_id": new_task.inserted_id}
        # )
        try:
            st_page_cls = StockController(request).stock_page()
            created_obj = await st_page_cls.create(stock_page)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (created_obj)
        return created_obj
    
    
    @router.patch("/{item_id}", response_model=StockPage)
    async def update_stock_page(request: Request, item_id: str, item: StockPageUpdate):
        updated_obj = None
        try:
            st_page_cls = StockController(request).stock_page()
            print ('##############', item)
            print ('$$$$$$$$', item_id)
            updated_obj = await st_page_cls.update(item_id, item)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (updated_obj)
        return updated_obj


    @router.get("/", response_description="List All the Stock Pages")
    async def posts(request: Request, name: Optional[str] = None):
        all_posts = []
        try:
            cls_obj = StockController(request).stock_page()
            query = {}
            if name:
                query['name'] = name
            all_objs = await cls_obj.get_all(query_params=query)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (all_objs)
        return all_objs
    

    @router.patch("/{item_id}", response_model=StockPage)
    async def update_item(item_id: str, item: StockPage):
        stored_item_data = items[item_id]
        stored_item_model = Item(**stored_item_data)
        update_data = item.dict(exclude_unset=True)
        updated_item = stored_item_model.copy(update=update_data)
        items[item_id] = jsonable_encoder(updated_item)
        return updated_item


    @router.patch("/update-position/{stock_id}/", response_model=StockPage, response_description="Update Position on Stock")
    async def update_position(request:Request, stock_id: str, position_type: str, email: EmailStr = Body(..., embed=True)):
        msg = ''
        try:
            params = {
                'stock_id': stock_id,
                'position_type': position_type
            }
            await UserController(request).update_st_position(email, params)
            cls_obj = StockController(request).stock_page()
            updated_obj = await cls_obj.update_position(stock_id, position_type)
            if updated_obj:
                return JSONResponse(status_code=status.HTTP_201_CREATED, content="Succefully Updated the StockPage Position")
            else:
                msg = ''
        except Exception as e:
                msg = str(e) 
        
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)
    
    @router.post("/join/", response_model=StockPage, response_description="Join Stock Page")
    async def join_stock_page(request: Request, stock_id: str, email: EmailStr = Body(..., embed=True)):
        st_page_data = await request.app.db["stockPage"].find_one({'_id': stock_id})
        if st_page_data:
            stock_name = st_page_data.get('name')
            created_time = datetime.now()
            subscribers = st_page_data.get('subscribers')
            if not isinstance(subscribers, int):
                subscribers = 0
            user_obj = await request.app.db["users"].find_one({'email': email})
            if user_obj:
                user_obj = await request.app.db["users"].update_one(
                    {'email': email}, 
                    {"$push": 
                        {'st_page_subscribed': {'name': stock_name, '_id': stock_id, 'joined_time': created_time}}
                    })
                stock_page = await request.app.db["stockPage"].update_one(
                    {'_id': stock_id}, 
                    {"$set": 
                        {"subscribers": int(subscribers) + 1}
                    })
            else:
                return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='User Doesnot Exist')
        else:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='Stock Page Doesnot Exist')
        
        return JSONResponse(status_code=status.HTTP_201_CREATED, content='User Joined Successfully')
    
    @router.get("/sentiment/", response_description="Get Sentiment Guage the Stock Pages")
    async def sentiment(request: Request, stock_id: str):
        all_posts = []
        try:
            cls_obj = StockController(request).stock_page()
            out = await cls_obj.get_sentiment(stock_id)        
        except Exception as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e)) 
        print (out)
        return out
    
    
    return router





def post_router(app):

    router = APIRouter()

    @router.post("/create", response_description="Add new Post", response_model=Post)
    async def create_post(
        request: Request, 
        image: UploadFile = File(None),
        post: Post = Body(...),
        # post: Post = Depends()
        # user: UserDB = Depends(app.fastapi_users.get_current_active_user)
    ):
        try:
            post_cls = StockController(request).post()
            created_post = await post_cls.create_post(post, image)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (create_post)
        return created_post
    
    @router.get("/", response_description="List All the Posts")
    async def posts(
        request: Request, 
        st_page: Optional[str] = None, 
        author: Optional[str] = None, 
        show_draft: bool = False,
        # user: UserDB = Depends(app.fastapi_users.get_current_active_user)
    ):
        all_posts = []
        try:
            # current_user = request.app.fastapi_users.get_current_active_user
            post_cls = StockController(request).post()
            posts = await post_cls.get_all(request.query_params)
            comment_cls = StockController(request).comment()
            for post in posts:
                count = await comment_cls.get_count(post.get('_id'))
                if count:
                    count = count[0]
                else:
                    count = 0
                post.update({
                    'num_comments': count
                })
                all_posts.append(post)

        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        return all_posts

    @router.get("/comments/{post_id}", response_description="List All the Comments under the Post")
    async def comments(request: Request, post_id: str):

        try:
            post_cls = StockController(request).comment()
            comments = await post_cls.get_all(post_id)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (comments)
        return comments

    @router.get("/user-thrust-point/", response_description="Get Thrust Point of the User Received")
    async def user_thrust_point(request: Request, user: Optional[str] = None):
        try:
            post_cls = StockController(request).post()
            thrust_points = await post_cls.get_user_thrust_point(user)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (thrust_points)
        return thrust_points

    @router.patch("/{post_id}/bookmark/", response_model=Post, response_description="Bookmark on Post")
    async def post_bookmark(request:Request, post_id: str, email: EmailStr = Body(..., embed=True)):
        msg = ''
        try:
            params = {
                'post_id': post_id,
            }
            await UserController(request).bookmark_post(email, params)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Post has been bookmarked.")
        except Exception as e:
                msg = str(e) 
        
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)
    
    @router.patch("/{post_id}/un-bookmark/", response_model=Post, response_description="Bookmark on Post")
    async def post_bookmark(request:Request, post_id: str, email: EmailStr = Body(..., embed=True)):
        msg = ''
        try:
            params = {
                'post_id': post_id,
            }
            await UserController(request).un_bookmark_post(email, params)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content="Bookamrked Post has been un-bookmarked.")
        except Exception as e:
                msg = str(e) 
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)


    @router.patch("/{post_id}/", response_model=Post, response_description="View Post")
    async def view_post(request:Request, post_id: str):
        msg = ''
        try:
            post_cls = StockController(request).post()
            post = await post_cls.get_post(post_id)
            print (post)
            return post
        except Exception as e:
                msg = str(e) 
        
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)


    @router.patch("/{post_id}/vote", response_model=Post, response_description="Vote on Post")
    async def vote_post(request:Request, post_id: str, vote_type: str):
        msg = ''
        try:
            post_cls = StockController(request).post()
            updated_obj = await post_cls.update_vote(post_id, vote_type)
            if updated_obj:
                return JSONResponse(status_code=status.HTTP_201_CREATED, content="Succefully Updated the Vote")
            else:
                msg = ''
        except Exception as e:
            msg = str(e)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)

    @router.put("/{post_id}", response_description="Update a Post")
    async def update_post(post_id: str, request: Request, post: UpdatePost = Body(...)):
        updated_obj = None
        try:
            cls_obj = StockController(request).post()
            updated_obj = await cls_obj.update(post_id, post)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        return updated_obj


    @router.post("/flairs/create", response_description="Add new Flair", response_model=Flair)
    async def create_flair(
        request: Request, 
        flair: Flair = Body(...),
        # user: UserDB = Depends(app.fastapi_users.get_current_active_user)
    ):
        try:
            obj_cls = StockController(request).flair()
            created_obj = await obj_cls.create(flair, user=user)
            print (created_obj)
        except Exception as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
        return created_obj
    
    @router.get("/flairs", response_description="List All the Flairs")
    async def flairs(
        request: Request, 
        # user: UserDB = Depends(app.fastapi_users.get_current_active_user)
    ):
        objs = []
        try:
            obj_cls = StockController(request).flair()
            objs = await obj_cls.get_all(request.query_params)
        except ValidationError as e:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
        
        return objs

    return router



def comment_router(app):

    router = APIRouter()

    @router.post("/create", response_description="Add new Comment", response_model=Comment)
    async def create_comment(request: Request, post: Comment = Body(...)):
        try:
            comment_cls = StockController(request).comment()
            created_comment = await comment_cls.create(post)
        except ValidationError as e:
            print ('>>>>>>>>>>>>>>>>')
            print(e)
        print (created_comment)
        return created_comment

    @router.patch("/{comment_id}/vote", response_model=Comment, response_description="Vote on Comment")
    async def vote_comment(request:Request, comment_id: str, vote_type: str):
        msg = ''
        try:
            comment_cls = StockController(request).comment()
            updated_obj = await comment_cls.update_vote(comment_id, vote_type)
            if updated_obj:
                return JSONResponse(status_code=status.HTTP_201_CREATED, content="Succefully Updated the Vote")
            else:
                msg = ''
        except Exception as e:
            msg = str(e)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=msg)

    return router


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@router.get("/")
async def get():
    return HTMLResponse(html)





    