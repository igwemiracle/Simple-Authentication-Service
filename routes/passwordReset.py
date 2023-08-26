import asyncio
import uuid
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from models.schemas import ForgotPassword, ResetPassword
from email_notification.send_email import EmailSender
from sqlalchemy.ext.asyncio import AsyncSession
from Database.connection import get_db
from routes import crud
from authenticate.hash_pwd import HashPassword
from fastapi.templating import Jinja2Templates


resetPassword = APIRouter()
hashThisPassword = HashPassword()
templates = Jinja2Templates(directory="templates")


@resetPassword.get("/auth/forgot_password")
async def renderForgotPasswordPage(request:Request):
    return templates.TemplateResponse("forgotPassword.html", {"request":request})

@resetPassword.post("/auth/forgot_password")
async def forgot_password(request: Request,
                          userEmail:str = Form(...),
                          db:AsyncSession=Depends(get_db)):
    
    if userEmail is None:
        error_msg = "User email is required."
        return templates.TemplateResponse("forgotPassword.html", {"request": request, "error_message": error_msg}, status_code=status.HTTP_400_BAD_REQUEST)
    #check if user exist
    user_exist = await crud.findUserExist(userEmail, db=db)
    if not user_exist:
        await asyncio.sleep(5)
        error_message = "User not found."
        return templates.TemplateResponse("forgotPassword.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)
        # raise HTTPException(status_code=404, detail="User not found")
    
    reset_code = str(uuid.uuid1())
    # try:
    await crud.createResetCode(userEmail, reset_code, db=db)
    # except Exception as e:
    #     error_message = "reset_code already exist for this email."
    #     raise HTTPException(status_code=400, detail=error_message)
    #sending email
    subject = 'Registration successful'
    recipient = [userEmail]
    content = """
<!DOCTYPE html>
<html>
<body style="margin:0; padding:0;box-sizing: border-box;font-family: Arial, Helvetica, sans-serif;">
    <div>
        <h1> Hello {0:}!</h1>
        <p>Someone has requested a link to reset your password. If you requested this,<br>you can change
        your password through the link below 👇.</p>
        <p><a href="http://127.0.0.1:8000/auth/reset_password/?reset_password_token={1:}">Reset Password link</a></p>
        <p>If you didn't request this, you can ignore this email.</p>
    </div>
</body>
</html>
    """.format(userEmail, reset_code)
    
    email_sender = EmailSender(subject, recipient, content)
    email_sender.send_email()
    # return {
    #     "reset_code": reset_code,
    #     "status_code": 200,
    #     "message": "We've sent an email with instructions to reset your password."
    # }
    return RedirectResponse(url="/auth/reset_password",
                            status_code=status.HTTP_303_SEE_OTHER)





@resetPassword.get("/auth/reset_password")
async def renderResetPasswordPage(request: Request):
    reset_password_token = request.query_params.get('reset_password_token')
    return templates.TemplateResponse("resetPassword.html", {"request": request, "reset_password_token": reset_password_token})


    # reset_password_token: str
    # new_password:str
    # confirm_password:str
@resetPassword.post("/auth/reset_password")
async def reset_password(request: Request,
                         new_password: str = Form(...),
                         confirm_password: str = Form(...),
                         reset_password_token: str = Form(...),
                          db:AsyncSession=Depends(get_db)):
    # check valid reset_password_token
    reset_token = await crud.check_reset_password_token(reset_password_token,db=db)
    if not reset_token:
        token_error_message = "Reset password token has expired, please request a new one."
        return templates.TemplateResponse("resetPassword.html", {"request": request, "token_error_message": token_error_message}, status_code=status.HTTP_404_NOT_FOUND)
        # raise HTTPException(status_code=404, detail="Reset password token has expired, please request a new one.")
    
    # check if new & confirm passwords are match
    if new_password != confirm_password:
        await asyncio.sleep(5)
        error_message = "new password and confirm_password do not match."
        return templates.TemplateResponse("resetPassword.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)
        # raise HTTPException(status_code=404, detail="New password is not match")

    # Reset new password

    forgot_password_object = ForgotPassword(id=reset_token[0][0],
                                            email=reset_token[0][1],
                                            token=reset_token[0][2],
                                            status=reset_token[0][3],
                                            timestamp=reset_token[0][4])
    new_hashed_password = hashThisPassword.create_hash(new_password)
    await crud.reset_password(new_hashed_password, forgot_password_object.email, db=db)

    #Disable reset code (already used)
    await crud.disable_reset_code(reset_password_token, forgot_password_object.email, db=db)
    return {
        "status_code": 200,
        "message": "Password has been reset successfully"
    }

#==================================================================================
# CODE 3
# @resetPassword.post("/account/login/forgot_password")
# async def forgot_password(request:ForgotPassword,
#                           db:AsyncSession=Depends(get_db)):
#     #check if user exist
#     user_exist = await crud.findUserExist(request.email, db=db)
#     if not user_exist:
#         await asyncio.sleep(5)
#         error_message = "User not found."
#         return templates.TemplateResponse("forgotPassword.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)
#         # raise HTTPException(status_code=404, detail="User not found")
    
#     reset_code = str(uuid.uuid1())
#     # try:
#     await crud.createResetCode(request.email, reset_code, db=db)
#     # except Exception as e:
#     #     error_message = "reset_code already exist for this email."
#     #     raise HTTPException(status_code=400, detail=error_message)
#     #sending email
#     subject = 'Registration successful'
#     recipient = [request.email]
#     content = """
# <!DOCTYPE html>
# <html>
# <body style="margin:0; padding:0;box-sizing: border-box;font-family: Arial, Helvetica, sans-serif;">
#     <div>
#         <h1> Hello {0:}!</h1>
#         <p>Someone has requested a link to reset your password. If you requested this,<br>you can change
#         your password through the link below 👇.</p>
#         <p><a href="http://127.0.0.1:8000/account/login/forgot_password/?reset_password_token={1:}">Reset Password link</a></p>
#         <p>If you didn't request this, you can ignore this email.</p>
#     </div>
# </body>
# </html>
#     """.format(request.email, reset_code)
    
#     email_sender = EmailSender(subject, recipient, content)
#     email_sender.send_email()
#     return {
#         "reset_code": reset_code,
#         "status_code": 200,
#         "message": "We've sent an email with instructions to reset your password."
#     }
#===================================================================================
# CODE 2
# @resetPassword.get("/account/login/reset_password")
# async def renderResetPasswordPage(request: Request):
#     return templates.TemplateResponse("resetPassword.html", {"request": request})


# @resetPassword.patch("/account/login/reset_password")
# async def reset_password(request:ResetPassword, db:AsyncSession=Depends(get_db)):
#     # check valid reset_password_token
#     reset_token = await crud.check_reset_password_token(request.reset_password_token,db=db)
#     if not reset_token:

#         raise HTTPException(status_code=404, detail="Reset password token has expired, please request a new one.")
    
#     # check if new & confirm passwords are match
#     if request.new_password != request.confirm_password:
#         await asyncio.sleep(5)
#         error_message = "New password is not match."
#         return templates.TemplateResponse("resetPassword.html", {"request": request, "error_message": error_message}, status_code=status.HTTP_404_NOT_FOUND)
#         # raise HTTPException(status_code=404, detail="New password is not match")

#     # Reset new password

#     forgot_password_object = ForgotPassword(id=reset_token[0][0],
#                                             email=reset_token[0][1],
#                                             token=reset_token[0][2],
#                                             status=reset_token[0][3],
#                                             timestamp=reset_token[0][4])
#     new_hashed_password = hashThisPassword.create_hash(request.new_password)
#     await crud.reset_password(new_hashed_password, forgot_password_object.email, db=db)

#     #Disable reset code (already used)
#     await crud.disable_reset_code(request.reset_password_token, forgot_password_object.email, db=db)
#     return {
#         "status_code": 200,
#         "message": "Password has been reset successfully"
#     }
