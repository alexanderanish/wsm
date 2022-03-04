from fastapi import APIRouter, Body, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .models import UserIn, UserOut, UpdateUserModel, get_password_hash
# from .controller import UserManager

router = APIRouter()

@router.post("/", response_description="Add new User", response_model=UserOut)
async def create_user(request: Request, user: UserIn = Body(...)):
    user = jsonable_encoder(user)
    username = user.get('username')
    password = get_password_hash('password')
    user['password'] = password
    if (has_user_exist := await request.app.mongodb["users"].find_one({"username": username})) is not None:
        raise HTTPException(status_code=409, detail=f"User already exist!")
    new_user = await request.app.mongodb["users"].insert_one(user)
    created_user = await request.app.mongodb["users"].find_one(
        {"_id": new_user.inserted_id}
    )


    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_user)



@router.get("/", response_description="List all Users")
async def list_users(request: Request):
    users = []
    for doc in await request.app.mongodb["users"].find().to_list(length=100):
        users.append(doc)
    return users


@router.get("/{id}", response_description="Get a single user")
async def show_user(id: str, request: Request):
    if (user := await request.app.mongodb["users"].find_one({"_id": id})) is not None:
        return user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.put("/{id}", response_description="Update a task")
async def update_user(id: str, request: Request, user: UpdateUserModel = Body(...)):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await request.app.mongodb["users"].update_one(
            {"_id": id}, {"$set": user}
        )

        if update_result.modified_count == 1:
            if (
                updated_task := await request.app.mongodb["users"].find_one({"_id": id})
            ) is not None:
                return updated_task

    if (
        existing_task := await request.app.mongodb["users"].find_one({"_id": id})
    ) is not None:
        return existing_task

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.delete("/{id}", response_description="Delete User")
async def delete_task(id: str, request: Request):
    delete_result = await request.app.mongodb["users"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"User {id} not found")