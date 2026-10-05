"""认证接口（见施工规范 §4.5）。"""
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.result import Result
from app.common.web_utils import client_ip
from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token
from app.schemas.auth import CaptchaResponse, LoginRequest, LoginResponse, RegisterRequest
from app.services import captcha_service, user_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/captcha")
def get_captcha():
    return Result(data=CaptchaResponse(**captcha_service.generate()))


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    captcha_service.verify(payload.captcha_id, payload.captcha_code)
    token, user = user_service.login(db, payload.username, payload.password, client_ip(request))
    return Result(data=LoginResponse(token=token, user=user))


@router.post("/register")
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    captcha_service.verify(payload.captcha_id, payload.captcha_code)
    user = user_service.register(db, payload.username, payload.password)
    token = create_access_token(user.username)
    return Result(data=LoginResponse(token=token, user=user))


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return Result(data=user_service.to_vo(current_user))
