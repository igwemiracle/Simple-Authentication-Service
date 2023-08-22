from fastapi import Depends, APIRouter, Form, Request, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from requests import Session
from Database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import UserCreate
from models.sqlDATA import User
from fastapi.templating import Jinja2Templates
from authenticate import cookie_auth
from authenticate.hash_pwd import HashPassword

hash_password = HashPassword()

signup = APIRouter()
templates = Jinja2Templates(directory="templates")


@signup.get("/")
async def renderHomePage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# @signup.get("/account")
# async def renderAccountPage(request: Request):
#     return templates.TemplateResponse("account.html", {"request": request})


@signup.get("/account")
async def render_account_page(request: Request, username: str):
    return templates.TemplateResponse(
        "account.html",
        {"request": request, "username": username}
    )


@signup.get("/register", response_class=HTMLResponse)
async def renderRegisterPage(request: Request, db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    print("")
    return templates.TemplateResponse("register.html", {"request": request, "users": users})


@signup.post("/register")
async def registerUser(request: Request,
                       username: str = Form(...),
                       email: str = Form(...),
                       password: str = Form(...),
                       confirm_password: str = Form(...),
                       db: AsyncSession = Depends(get_db)):
    if password != confirm_password:
        error_msg = "Invalid password,please confirm password again."
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_msg": error_msg}
        )
    dbUser = User(username=username, email=email,
                  hash_password=password, confirm_password=confirm_password)
    db.add(dbUser)
    await db.commit()
    await db.refresh(dbUser)
    return RedirectResponse(url=f"/account?username={username}",
                            status_code=status.HTTP_303_SEE_OTHER)
