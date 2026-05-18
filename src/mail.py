from fastapi_mail import MessageType, MessageSchema, FastMail, ConnectionConfig
from config import settings as s
from typing import List

config = ConnectionConfig(
    MAIL_USERNAME=s.MAIL_USERNAME,
    MAIL_PASSWORD=s.MAIL_PASSWORD,
    MAIL_FROM=s.MAIL_FROM,
    MAIL_PORT=s.MAIL_PORT,
    MAIL_SERVER=s.MAIL_SERVER,
    MAIL_FROM_NAME=s.MAIL_FROM_NAME,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    VALIDATE_CERTS=False,
    TEMPLATE_FOLDER="./template",
)


mail = FastMail(config=config)


async def create_message(recipients: List[str], subject: str, body: str):
    message = MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )
    return message
