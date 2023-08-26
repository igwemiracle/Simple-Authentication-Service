
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

home = APIRouter()
templates = Jinja2Templates(directory="templates")


@home.get("/")
async def renderHomePage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})