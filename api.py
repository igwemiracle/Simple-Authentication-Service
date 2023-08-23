from fastapi import FastAPI
import uvicorn
from routes.signup import signup
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(signup)
app.mount("/static",
          StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port="8080")
