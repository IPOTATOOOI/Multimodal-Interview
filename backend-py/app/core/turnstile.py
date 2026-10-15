import httpx
from app.core.config import settings

async def validate_turnstile_token(token: str) -> dict:
    """
    验证 Cloudflare Turnstile 令牌
    
    Args:
        token: 前端传递的 Turnstile 验证令牌
    
    Returns:
        dict: 包含验证结果和错误信息的字典
    """
    if not token:
        return {"success": False, "error": "缺少 Turnstile 验证令牌"}
    
    if not settings.CF_TURNSTILE_SECRET_KEY:
        return {"success": False, "error": "Turnstile 密钥未配置"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.CF_TURNSTILE_SECRET_KEY,
                    "response": token
                }
            )
            
        result = response.json()
        
        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            return {"success": False, "error": f"Turnstile 验证失败: {error_codes}"}
        
        return {"success": True}
        
    except httpx.RequestError as e:
        return {"success": False, "error": f"验证服务连接失败: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"验证失败: {str(e)}"}