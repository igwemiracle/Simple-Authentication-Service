from fastapi import Depends, APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from Database.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.sqlDATA import User
from fastapi.templating import Jinja2Templates
from authenticate.hash_pwd import HashPassword
from routes import crud


hashThisPassword = HashPassword()

signup = APIRouter()
templates = Jinja2Templates(directory="templates")

@signup.get("/")
async def renderHomePage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@signup.get("/account")
async def render_account_page(request: Request, username: str = None, loggedin: bool = False):
    return templates.TemplateResponse(
        "account.html",
        {"request": request, "username": username, "loggedin": loggedin}
    )


@signup.get("/account/register", response_class=HTMLResponse)
async def renderRegisterPage(request: Request, db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    return templates.TemplateResponse("register.html", {"request": request, "users": users})


@signup.post("/account/register")
async def registerUser(request: Request,
                       username: str = Form(...),
                       email: str = Form(...),
                       password: str = Form(...),
                       confirm_password: str = Form(...),
                       db: AsyncSession = Depends(get_db)):

    user_exist = await crud.find_user_exist(email=email, db=db)
    if user_exist:
        error_message = "Email already exists. Please use a different email."
        return templates.TemplateResponse(
        "register.html",
        {"request": request, "error_message": error_message},
        status_code=status.HTTP_400_BAD_REQUEST,
    )

    if password != confirm_password:
        error_msg = "Invalid password,please confirm password again."
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_msg": error_msg},
        status_code=status.HTTP_404_NOT_FOUND)
    # Hash my password
    hashed_password = hashThisPassword.create_hash(password)
    confirm_hash = hashThisPassword.create_hash(confirm_password)
    dbUser = User(username=username, email=email,
                  hash_password=hashed_password, confirm_password=confirm_hash)
    db.add(dbUser)
    await db.commit()
    await db.refresh(dbUser)
    return RedirectResponse(url=f"/account?username={username}&loggedin=True",
                            status_code=status.HTTP_303_SEE_OTHER)
