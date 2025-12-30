from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils import decode_token
from fastapi import HTTPException


class TokenBearer(HTTPBearer):
    def __init__(
        self, *, bearerFormat=None, scheme_name=None, description=None, auto_error=True
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request):
        cred = await super().__call__(request)
        token = cred.credentials
        token_data = await decode_token(token)
        if token_data is None:
            raise HTTPException(status_code=403, detail="Invalid Token")

        self.verify_token(token_data)
        return token_data

    def verify_token(self, token_data):
        raise NotImplementedError()


class AccessTokenBearer(TokenBearer):
    def verify_token(token_data: str):
        if token_data["refresh"]:
            raise HTTPException(status_code=403, detail="Access Token Required")


class RefreshTokenBearer(TokenBearer):
    def verify_token(token_data: str):
        if not token_data["refresh"]:
            raise HTTPException(status_code=403, detail="Refresh Token Required")
