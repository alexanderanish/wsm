import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from starlette.responses import JSONResponse
from starlette.background import BackgroundTasks

from dotenv import load_dotenv
load_dotenv('.env')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIN_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
    # TEMPLATE_FOLDER='./templates/email'
)


async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        # subtype='html',
    )
    fm = FastMail(conf)
    await fm.send_message(message)


def send_email_background(subject: str, email_to: str, body: dict):
    background_tasks = BackgroundTasks()
    # print (background_tasks)
    # print (subject)
    # print (email_to)
    # print (body)
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        # subtype='html',
    )
    fm = FastMail(conf)
    # print ('Message >>>>>>>')
    # print (conf)
    # print (message)
    # task = BackgroundTask(fm.send_message, message)
    background_tasks.add_task(fm.send_message, message)
    message = {'status': 'Email Sent Successfully'}
    return JSONResponse(message, background=background_tasks)


def send_password_reset_email(background_tasks: BackgroundTasks, email: str, token: str):
    print ('>>>>>>>>', email, token)
    send_email_background(background_tasks, 'WSM Project',   
        'azarmhmd21@gmail.com', "title: 'Hello World', 'name':'John Doe'")
    print ('Email Sent Successful >>>>')

# def sample_test():
