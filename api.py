from fastapi import FastAPI
import uvicorn
from routes.home import home
from routes.register import register
from routes.login import login
from routes.account import account
from routes.passwordReset import resetPassword
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(home)
app.include_router(register)
app.include_router(login)
app.include_router(resetPassword)
app.include_router(account)
app.mount("/static",
          StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8080")

# /Users/apple/Desktop/Miracle/unfinished/SQL/static/images/bottom_img.png