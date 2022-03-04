from fastapi import Body, HTTPException, status
from fastapi_users import models
from fastapi_users.db import BaseUserDatabase
from fastapi_users.utils import JWT_ALGORITHM, generate_jwt
from config import settings
from fastapi_users.router.common import ErrorCode
from pydantic import UUID4, EmailStr
from apps.util.utils import safe_open_w
import jwt
import shutil

class UserVerification:
    VERIFICATION_TOKEN_AUDIENCE = 'fastapi-users:verification'
    TOKEN_LIFETIME_SECONDS = 3600

    async def request_verification(user: str):
        
        if user:
            token_data = {"user_id": str(user), "aud": UserVerification.VERIFICATION_TOKEN_AUDIENCE}
            token = generate_jwt(
                token_data,
                UserVerification.TOKEN_LIFETIME_SECONDS,
                settings.JWT_SECRET_KEY,
            )
            return token

        return None

    async def verify_token(user_db: BaseUserDatabase[models.BaseUserDB], token: str = Body(...)):
        try:
            print ('Verfy Token >>>>>>>>>>')
            data = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                audience=UserVerification.VERIFICATION_TOKEN_AUDIENCE,
                algorithms=[JWT_ALGORITHM],
            )
            user_id = data.get("user_id")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )
            try:
                user_uiid = UUID4(user_id)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )
            print (user_db)
            user = await user_db.get(user_uiid)
            if user is None or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
                )
            user.has_verified = True
            await user_db.update(user)
            return True
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
            )


async def save_to_files(file_obj, folder_name=None):
    file_location = f"static/"
    if folder_name:
        file_location += folder_name + "/"
    with safe_open_w(file_location + file_obj.filename) as file_object:
        shutil.copyfileobj(file_obj.file, file_object)