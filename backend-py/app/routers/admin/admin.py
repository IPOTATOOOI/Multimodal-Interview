from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query
from datetime import timedelta

from app.models.admin import AdminCreateUser
from app.services.admin.admin import AdminService
from app.controller.auth import create_access_token, get_current_admin
from app.core.config import settings
# from app.core.turnstile import validate_turnstile_token  # 注释掉 Cloudflare 人机验证

router = APIRouter(tags=["管理员"])

# 注释掉 Cloudflare 人机验证相关代码
# # Add Turnstile validation endpoint
# @router.post("/admin/verify-turnstile")
# async def verify_turnstile(cf_turnstile_response: str = Form(...)):
#     """
#     验证 Cloudflare Turnstile 令牌
#     - cf_turnstile_response: Turnstile 验证令牌
#     """
#     result = await validate_turnstile_token(cf_turnstile_response)
#     return result


@router.get("/admin/dashboard/stats")
async def get_dashboard_stats():
    """
    获取大屏统计数据
    """
    try:
        stats = AdminService.get_dashboard_stats()
        return {"code": 200, "message": "success", "data": stats}
    except HTTPException as e:
        return {"code": e.status_code, "message": e.detail}


@router.get("/admin/dashboard/interviews")
async def get_dashboard_interviews():
    """
    获取大屏展示所需的所有面试数据（一次性查询，避免逐个用户请求）
    """
    try:
        data = AdminService.get_all_interviews_for_dashboard()
        return {"code": 200, "message": "success", "data": data}
    except HTTPException as e:
        return {"code": e.status_code, "message": e.detail}
    except Exception as e:
        return {"code": 500, "message": f"获取面试数据失败: {str(e)}", "data": None}



@router.post("/admin/register", status_code=201)
async def register_admin(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    admin_code: str = Form(...),
    # cf_turnstile_response: str = Form(...),  # 注释掉 Cloudflare 人机验证参数
    face: UploadFile = File(None),
):
    """
    管理员注册接口（multipart/form-data）
    - username: 用户名
    - password: 密码
    - email: 邮箱
    - admin_code: 管理员注册码
    # - cf_turnstile_response: Turnstile 验证令牌  # 注释掉
    - face: 可选，人脸图片文件
    """
    # 注释掉 Cloudflare 人机验证代码
    # # Validate Turnstile token
    # turnstile_result = await validate_turnstile_token(cf_turnstile_response)
    # if not turnstile_result["success"]:
    #     raise HTTPException(status_code=400, detail=turnstile_result["error"])
    
    # 验证管理员注册码
    valid_codes = {
        code.strip()
        for code in settings.ADMIN_REGISTRATION_CODES.split(",")
        if code.strip()
    }
    if not valid_codes:
        raise HTTPException(status_code=503, detail="管理员注册功能尚未配置")
    if admin_code not in valid_codes:
        raise HTTPException(status_code=401, detail="无效的管理员注册码")
    
    # 读取文件内容（如果有）并传给服务层
    face_bytes = None
    if face is not None:
        face_bytes = await face.read()
        orig_filename = face.filename
    else:
        orig_filename = None

    admin_data = AdminService.register_admin({
        "username": username,
        "password": password,
        "email": email,
        "face_original_filename": orig_filename,
        "face_bytes": face_bytes
    })
    return {
        "code": 200,
        "message": "操作成功",
        "data": admin_data
    }

@router.post("/admin/login")
async def login_admin(
    username: str = Form(...),
    password: str = Form(...),
    # cf_turnstile_response: str = Form(...)  # 注释掉 Cloudflare 人机验证参数
):
    """
    管理员登录接口（multipart/form-data）
    - username: 用户名
    - password: 密码
    # - cf_turnstile_response: Turnstile 验证令牌  # 注释掉
    """
    # 注释掉 Cloudflare 人机验证代码
    # # Validate Turnstile token
    # turnstile_result = await validate_turnstile_token(cf_turnstile_response)
    # if not turnstile_result["success"]:
    #     raise HTTPException(status_code=400, detail=turnstile_result["error"])
    
    auth_admin = AdminService.authenticate_admin(username, password)
    access_token = create_access_token(
        data={"sub": username, "is_admin": True},
        expires_delta=timedelta(hours=24)
    )
    return {
        "code": 200,
        "message": "操作成功",
        "data": access_token,
        "access_token": access_token,
        "token_type": "bearer",
        "is_admin": True,
        "user_id": auth_admin["id"]
    }


@router.post("/admin/users")
async def create_user(
    user_data: AdminCreateUser,
    current_admin: dict = Depends(get_current_admin)
):
    created_user = AdminService.create_user(user_data.model_dump())
    return {
        "code": 200,
        "message": "操作成功",
        "data": created_user
    }


@router.get("/admin/users")
async def list_users(
    username: str = Query(None, description="按用户名模糊查询"),
    current_admin: dict = Depends(get_current_admin)
):
    data = AdminService.list_users(username=username)
    return {
        "code": 200,
        "message": "操作成功",
        "data": data
    }


@router.get("/admin/users/by-username/{username}")
async def get_user_by_username(
    username: str,
    current_admin: dict = Depends(get_current_admin)
):
    user = AdminService.get_user_by_username(username)
    return {
        "code": 200,
        "message": "操作成功",
        "data": user
    }


@router.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    current_admin: dict = Depends(get_current_admin)
):
    deleted_user = AdminService.delete_user(user_id)
    return {
        "code": 200,
        "message": "操作成功",
        "data": deleted_user
    }
