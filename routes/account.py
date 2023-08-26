
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

account = APIRouter()
templates = Jinja2Templates(directory="templates")


@account.get("/account")
async def render_account_page(request: Request, username: str = None, loggedin: bool = False):
    return templates.TemplateResponse(
        "account.html",
        {"request": request, "username": username, "loggedin": loggedin}
    )