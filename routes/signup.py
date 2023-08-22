from fastapi import Depends, APIRouter, Form, Request, status, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
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


@signup.get("/account")
async def renderAccountPage(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})
# =========================================================================


@signup.get("/register", response_class=HTMLResponse)
async def renderRegisterPage(request: Request, db: AsyncSession = Depends(get_db)):
    results = await db.execute(select(User))
    users = results.scalars().all()
    print("")
    # return {"users": users}
    return templates.TemplateResponse("register.html", {"request": request, "users": users})


@signup.post("/register")
async def registerUser(request: Request,
                       username: str = Form(...),
                       email: str = Form(...),
                       password: str = Form(...),
                       confirm_password: str = Form(...),
                       db: AsyncSession = Depends(get_db)):
    if password != confirm_password:
        error_msg = "Invalid password,please confirm password."
        return templates.TemplateResponse(
            "base.html",
            {"request": request, "error_msg": error_msg}
        )
    dbUser = User(username=username, email=email,
                  hash_password=password, confirm_password=confirm_password)
    db.add(dbUser)
    await db.commit()
    await db.refresh(dbUser)
    print('user added')
    return RedirectResponse(url="/",
                            status_code=status.HTTP_303_SEE_OTHER)
# =========================================================================
# @signup.get("/user")
# async def read_users(db: AsyncSession = Depends(get_db)):
#     results = await db.execute(select(User))
#     users = results.scalars().all()
#     return {"users": users}


# @signup.post("/user")
# async def get_users(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     if user.password != user.confirm_password:
#         return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid password.")

#     db_user = User(username=user.username, email=user.email,
#                    hash_password=user.password, confirm_password=user.confirm_password)
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user
# ============================================================================


# =========================================================================

# @signup.get("/account/logout")
# async def signout():
#     response = RedirectResponse(
#         url="/", status_code=status.HTTP_302_FOUND)
#     return response
