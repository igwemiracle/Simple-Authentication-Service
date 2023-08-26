from typing import List
from fastapi import Depends, APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from Database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from routes.crud import createRegisteredUser
from models.sqlDATA import User
from fastapi.templating import Jinja2Templates
from authenticate.hash_pwd import HashPassword
from routes import crud


hashThisPassword = HashPassword()

register = APIRouter()
templates = Jinja2Templates(directory="templates")



@register.get("/auth/register", response_class=HTMLResponse)
async def renderRegisterPage(request: Request, db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    return templates.TemplateResponse("register.html", {"request": request, "users": users})



@register.post("/auth/register")
async def registerUser(request: Request,
                       username: str = Form(...),
                       email: str = Form(...),
                       password: str = Form(...),
                       confirm_password: str = Form(...),
                       db: AsyncSession = Depends(get_db)):
    # Checks If User exist
    user_exist = await crud.findUserExist(email=email, db=db)
    if user_exist:
        error_message = "User with email already exists.Please use a different email."
        return templates.TemplateResponse(
        "register.html",
        {"request": request, "error_message": error_message},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

    # Checks if both Passwords are same
    if password != confirm_password:
        error_msg = "Passwords do not match."
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_msg": error_msg},
        status_code=status.HTTP_404_NOT_FOUND)
    hashed_password = hashThisPassword.create_hash(password)
    # Creates the User and adds to database
    dbUser = await createRegisteredUser(username, email, hashed_password, db)
    db.add(dbUser)
    await db.commit()
    await db.refresh(dbUser)
    return RedirectResponse(url=f"/account?username={username}&loggedin=True",
                            status_code=status.HTTP_303_SEE_OTHER)

#==================================================================
# @signup.post("/account/register")
# async def registerUser(request: Request,
#                        username: str = Form(...),
#                        email: str = Form(...),
#                        password: str = Form(...),
#                        confirm_password: str = Form(...),
#                        db: AsyncSession = Depends(get_db)):

#     user_exist = await crud.find_user_exist(email=email, db=db)
#     if user_exist:
#         error_message = "User with email already exists.Please use a different email."
#         return templates.TemplateResponse(
#         "register.html",
#         {"request": request, "error_message": error_message},
#         status_code=status.HTTP_400_BAD_REQUEST,
#     )

#     if password != confirm_password:
#         error_msg = "Invalid password,please confirm password again."
#         return templates.TemplateResponse(
#             "register.html",
#             {"request": request, "error_msg": error_msg},
#         status_code=status.HTTP_404_NOT_FOUND)
#     # Hash my password
#     hashed_password = hashThisPassword.create_hash(password)
#     confirm_hash = hashThisPassword.create_hash(confirm_password)
#     dbUser = User(username=username, email=email,
#                   hash_password=hashed_password, confirm_password=confirm_hash)
#     db.add(dbUser)
#     await db.commit()
#     await db.refresh(dbUser)
#     return RedirectResponse(url=f"/account?username={username}&loggedin=True",
#                             status_code=status.HTTP_303_SEE_OTHER)
