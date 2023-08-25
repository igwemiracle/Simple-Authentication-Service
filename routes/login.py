import asyncio
import uuid
from fastapi import Depends, APIRouter, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from Database.connection import get_db
from models.schemas import ForgotPassword
from authenticate.hash_pwd import HashPassword
from authenticate import cookie_auth
from routes import crud
from email_notification.send_email import EmailSender



hashThisPassword = HashPassword()


templates = Jinja2Templates(directory="templates")
login = APIRouter()



@login.get("/account/login")
async def renderLoginPage(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@login.post("/account/login")
async def loginPage(request: Request,
                    email: str = Form(...),
                    password: str = Form(...), db: AsyncSession = Depends(get_db)):
    user = await crud.find_user_exist(email=email, db=db)
    if not user:
        await asyncio.sleep(5)
        error_message = "The account does not exist or the password is wrong."
        return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)

    if not hashThisPassword.verify_hash(password, user.hash_password):
        error_message = "The account does not exist or the password is wrong."
        return templates.TemplateResponse("login.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)

    response = RedirectResponse(
        url=f"/account?username={user.username}&loggedin=True",  status_code=status.HTTP_302_FOUND)
    cookie_auth.set_auth(response, user.id)
    return response


@login.get("/account/logout")
async def renderLogoutPage():
    response = RedirectResponse(
        url="/", status_code=status.HTTP_302_FOUND
    )
    cookie_auth.logout(response)
    return response
