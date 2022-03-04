from fastapi import APIRouter, Request, Depends, BackgroundTasks, Body, status, HTTPException, Response, FastAPI, UploadFile, File
from config import settings
from fastapi.security import OAuth2PasswordRequestForm
from .models import UserDB, UserCreate, UserView, UserUpdate, User,UserAdditionalUpdate
from .auth import jwt_authentication
from .utils import UserVerification, save_to_files
from fastapi_users.models import BaseUser
from apps.util.email_configuration import send_email_background,send_email_async, send_password_reset_email
from apps.util.utils import generate_otp, safe_open_w
from pydantic import UUID4, EmailStr
from fastapi_users.db import BaseUserDatabase
from fastapi_users import models
# from .fastapi_users_copy import get_users_router
from typing import Callable, Optional, Type
from fastapi_users.user import CreateUserProtocol, UserAlreadyExists, get_create_user
from fastapi_users.router.common import ErrorCode
import datetime
from starlette.responses import JSONResponse
from fastapi_users.password import get_password_hash
from .common import UserController
from apps.auth.auth_bearer import has_access
from fastapi_users import models
import shutil



import asyncio

router = APIRouter()



def get_users_router(app):
    users_router = APIRouter()

    def on_after_register(user: UserDB, request: Request):
        print(f"User {user.id} has registered.")
        # await send_email_async('Hello World','azarmhmd21@gmail.com',
        #         "title: 'Hello World', 'name':       'John Doe'")

    def on_after_forgot_password(user: UserDB, token: str, request: Request):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(send_email_async('Hello World','azarmhmd21@gmail.com',
                "title: 'Hello World', 'name':       'John Doe'"))
        loop.close()
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        return send_email_background('Hello World','azarmhmd21@gmail.com',
                "title: 'Hello World', 'name':       'John Doe'")
        

    users_router.include_router(
        app.fastapi_users.get_auth_router(jwt_authentication),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    # users_router.include_router(
    #     app.fastapi_users.get_register_router(on_after_register),
    #     prefix="/auth",
    #     tags=["auth"],
    # )
    # users_router.include_router(
    #     app.fastapi_users.get_reset_password_router(
    #         settings.JWT_SECRET_KEY, after_forgot_password=on_after_forgot_password
    #     ),
    #     prefix="/auth",
    #     tags=["auth"],
    # )
    users_router.include_router(
        app.fastapi_users.get_users_router(), prefix="/users", tags=["users"]
    )

    
    # @users_router.get("/users/")
    # async def list_users(
    #     request: Request,
    #     user: UserDB = Depends(app.fastapi_users.get_current_active_user),
    # ):
    #     tasks = []
    #     for doc in await request.app.db["users"].find().to_list(length=100):
    #         doc.pop('hashed_password')
    #         doc.pop('_id')
    #         print (doc)
    #         tasks.append(doc)
    #     return tasks

    
    
    return users_router
    

@router.get("/users/")
async def list_users(
    request: Request,
    page_size: int = 10,
    page_no: int = 1,
    search_key: Optional[str] = None,
    # user: UserDB = Depends(Request.app.fastapi_users.get_current_active_user)
    
):
    payload = {}
    if search_key:
        payload['search_key'] = search_key
    users = await UserController(request).get_users(page_size, page_no, payload)
    return users


@router.get("/users/view-user/{email}", response_model=UserView, status_code=status.HTTP_201_CREATED)
async def list_users(
    request: Request,
    email: str
    # user: UserDB = Depends(Request.app.fastapi_users.get_current_active_user)
    
):
    
    user = await request.app.fastapi_users.db.get_by_email(email)
    return user

@router.patch(
        "/users/{id}/profile-pic-update/",
    )
async def update_user(
    id: UUID4, request: Request, profile_picture: UploadFile = File(None)  # type: ignore
):
    try:
        await UserController(request).update_profile_pic(id, profile_picture)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content='User Profile picture has been successfully updated.')
        # user = await request.app.fastapi_users.db.get(id)
        # if user is None:
        #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        # await save_to_files(profile_picture, 'profile-pic')
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
    return []


@router.post("/login")
async def login(
    request: Request, response: Response, credentials: OAuth2PasswordRequestForm = Depends()
):
    user = await request.app.fastapi_users.db.authenticate(credentials)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    elif not user.has_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User has not verified the account registered!',
        )
    s = await jwt_authentication.get_login_response(user, response)
    print (s)
    return s


@router.post('/forgot-password')
async def forgot_password(
        request: Request, email: EmailStr = Body(..., embed=True)
    ):
    print ('Email >>>>>>>>>', email)
   
    user = await request.app.fastapi_users.db.get_by_email(email)
    if user is not None and user.is_active:
        otp = generate_otp()
        otp_obj_payload = {
            'email': email,
            'otp': otp,
            'date_created': datetime.datetime.now(),
        }
        otp_obj = await request.app.db["otp"].insert_one(otp_obj_payload)
        return send_email_background('Request Password Reset - OTP has been received', 'azarmhmd21@gmail.com',
                "Hi, \n\n Your Password reset process has been initiated. Please find the OTP as below \n OTP: %s \n\n Thanks & Regards,\n WSM Team" % (otp, ))

    
    return None

@router.post("/reset-password")
async def reset_password(request: Request, email: EmailStr = Body(..., embed=True), otp: str = Body(...), password: str = Body(...)):
    try:
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User Email Should not empty',
            )
        try:
            user = await request.app.fastapi_users.db.get_by_email(email)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='User Doesnot exist or not active',
                )
        except Exception:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='User Doesnot exist',
                )
        print ('3333333')
        record = request.app.db["otp"].find({"email": email}).sort("_id",-1).limit(1)
        has_otp_matched = False
        for document in await record.to_list(length=100):
            existing_otp = document.get('otp')
            if str(otp) == str(existing_otp):
                has_otp_matched = True
        print ('4444444', has_otp_matched)
        
        if has_otp_matched:
            user.hashed_password = get_password_hash(password)
            await request.app.fastapi_users.db.update(user)
            return JSONResponse({'msg': 'Password Changed Successfully!'})
        else:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='OTP entered is incorrect!',
                )
    except Exception as e:
        print (e)
        raise e



@router.post(
    "/register-user",  response_model=BaseUser, status_code=status.HTTP_201_CREATED
)
async def register(request: Request, user: UserCreate):  # type: ignore
    try:
        user_db_model = Type[models.BaseUserDB]
        print (user)
        created_user = await request.app.fastapi_users.create_user(user)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )

    if created_user:
        token = await UserVerification.request_verification(created_user.id)
        print (token)
        client_host = request.client.host
        path = 'http://' + client_host + ':8000/auth/verify-user/?token=' + token
        return send_email_background('User Account Created - WSM', 'azarmhmd21@gmail.com',
                "Hey, \n\n Your account has been created.\n\n A sign in attempt requires further verification. \n\n Please click the below url to verify. \n %s \n\n Thanks & Regards,\n WSM Team" 
                % (path, ))


    return created_user


@router.post("/verify-user")
async def verify_user(request: Request, token: str = Body(...)):
    try:
        has_verified = await UserVerification.verify_token(request.app.fastapi_users.db, token)
        print ('$$$$$Has Verified >>>>', has_verified)
        return JSONResponse({'msg': 'User Successfully Verified'})
    except Exception as e:
        return e


    