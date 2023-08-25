from pydantic import BaseModel

# PYDANTIC


class UserCreate(BaseModel):
    id: int
    username: str
    email: str
    hash_password: str
    confirm_password: str
    is_logged_in: bool

class ForgotPassword(BaseModel):
    email:str