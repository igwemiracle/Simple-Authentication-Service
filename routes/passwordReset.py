import uuid
from fastapi import APIRouter, Depends, HTTPException
from models.schemas import ForgotPassword
from email_notification.send_email import EmailSender
from sqlalchemy.ext.asyncio import AsyncSession
from Database.connection import get_db
from routes import crud


resetPassword = APIRouter()

@resetPassword.post("/account/login/forgot_password")
async def forgot_password(request:ForgotPassword,
                          db:AsyncSession=Depends(get_db)):
    #check if user exist
    user_exist = await crud.find_user_exist(request.email, db=db)
    if not user_exist:
        raise HTTPException(status_code=404, detail="User not found")
    
    reset_code = str(uuid.uuid1())
    try:
        await crud.create_reset_code(request.email, reset_code, db=db)
    except Exception as e:
        # Handle other exceptions that might occur during the process
        error_message = "reset_code already exist for this email."
        raise HTTPException(status_code=400, detail=error_message)
    #sending email
    subject = 'Register successful'
    recipient = [request.email]
    content = """
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0;box-sizing: border-box;font-family: Arial, Helvetica, sans-serif;">
    <div>
        <h1> Hello {0:}!</h1>
        <p>Someone has requested a link to reset your password. If you requested this, you can change
        your password through the link below</p>
        <a href="http://127.0.0.1:8000/account/login/forgot_password/?reset_password_token={1:}"></a>
        <p>If you didn't request this, you can ignore this email.</p>
    </div>
</body>
</html>
    """.format(request.email, reset_code)
    
    email_sender = EmailSender(subject, recipient, content)
    email_sender.send_email()
    return {
        "reset_code": reset_code,
        "status_code": 200,
        "message": "We've sent an email with instructions to reset your password."
    }
