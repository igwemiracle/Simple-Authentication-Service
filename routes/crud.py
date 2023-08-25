import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Database.connection import get_db 
from models.sqlDATA import User, ResetCode
from sqlalchemy import select, insert


async def find_user_exist(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar()

async def create_reset_code(email:str, reset_code:str, db:AsyncSession=Depends(get_db)):
    query = insert(ResetCode).values(
        email=email,
        reset_code=reset_code,
        status='1', 
        expired_in=datetime.datetime.utcnow()
        )
    await db.execute(query)
    await db.commit()