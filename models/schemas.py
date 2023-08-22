from pydantic import BaseModel

# PYDANTIC


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str
