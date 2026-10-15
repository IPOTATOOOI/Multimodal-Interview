from fastapi import APIRouter, status, Depends, UploadFile, File, Form, HTTPException, Request
from pydantic import BaseModel
from app.SchemasAuth import UserLogin, Token, UserResponse
from app.controller.auth import AuthService, get_current_user, create_access_token
# from app.core.turnstile import validate_turnstile_token  # 注释掉 Cloudflare 人机验证
from datetime import timedelta

router = APIRouter(tags=["认证"])

# 注释掉 Cloudflare 人机验证相关代码
# class TurnstileRequest(BaseModel):
#     cf_turnstile_response: str

# # Add Turnstile validation endpoint
# @router.post("/verify-turnstile")
# async def verify_turnstile(request: TurnstileRequest):
#     """
#     验证 Cloudflare Turnstile 令牌
#     - cf_turnstile_response: Turnstile 验证令牌
#     """
#     result = await validate_turnstile_token(request.cf_turnstile_response)
#     return result

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    # cf_turnstile_response: str = Form(...),  # 注释掉 Cloudflare 人机验证参数
    admin_code: str = Form(None),
    face: UploadFile = File(None),
):
    """
    注册接口（multipart/form-data）
    - username: 用户名
    - password: 密码
    - email: 邮箱
    # - cf_turnstile_response: Turnstile 验证令牌  # 注释掉
    - admin_code: 管理员注册码（仅管理员注册时需要）
    - face: 可选，人脸图片文件
    """
    # 注释掉 Cloudflare 人机验证代码
    # # Validate Turnstile token
    # turnstile_result = await validate_turnstile_token(cf_turnstile_response)
    # if not turnstile_result["success"]:
    #     raise HTTPException(status_code=400, detail=turnstile_result["error"])
    
    # 读取文件内容（如果有）并传给服务层，由服务层保存文件并写入数据库
    face_filename = None
    face_bytes = None
    if face is not None:
        face_bytes = await face.read()
        orig_filename = face.filename
    else:
        orig_filename = None

    AuthService.register_user(username=username, password=password, email=email, face_original_filename=orig_filename, face_bytes=face_bytes)
    return {"message": "用户注册成功"}

@router.post("/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    # cf_turnstile_response: str = Form(...)  # 注释掉 Cloudflare 人机验证参数
):
    """
    登录接口（multipart/form-data）
    - username: 用户名
    - password: 密码
    # - cf_turnstile_response: Turnstile 验证令牌  # 注释掉
    """
    # 注释掉 Cloudflare 人机验证代码
    # # Validate Turnstile token
    # turnstile_result = await validate_turnstile_token(cf_turnstile_response)
    # if not turnstile_result["success"]:
    #     raise HTTPException(status_code=400, detail=turnstile_result["error"])
    
    # Create UserLogin object
    user = UserLogin(username=username, password=password)
    
    auth_user = AuthService.authenticate_user(user)
    access_token = create_access_token(
        data={"sub": auth_user["username"]},
        expires_delta=timedelta(minutes=30)
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": auth_user["user_id"]
    }

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "created_at": current_user["created_at"]
    }


@router.get("/ip")
async def get_client_ip(request: Request):
    """获取当前请求的客户端IP地址。"""
    # 反向代理场景优先取 X-Forwarded-For 的首个IP
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        real_ip = request.headers.get("x-real-ip")
        client_ip = real_ip.strip() if real_ip else (request.client.host if request.client else None)

    return {
        "ip": client_ip
    }