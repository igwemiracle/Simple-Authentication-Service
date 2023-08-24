from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Database.connection import get_db
from models.sqlDATA import User
from sqlalchemy import select


async def find_user_exist(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar()
