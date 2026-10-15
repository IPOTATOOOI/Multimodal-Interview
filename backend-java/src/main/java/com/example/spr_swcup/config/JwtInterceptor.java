package com.example.spr_swcup.config;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.security.SignatureException;
import io.jsonwebtoken.UnsupportedJwtException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

/**
 * JWT 拦截器：验证管理员接口的请求令牌合法性
 */
@Component // 必须加@Component，让Spring扫描到并注入到WebMvcConfig中
public class JwtInterceptor implements HandlerInterceptor {

    // 注入之前编写的JwtUtil工具类，用于令牌解析和验证
    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 拦截器核心方法：请求处理前执行（验证令牌）
     * @param request  请求对象（用于获取请求头中的JWT）
     * @param response 响应对象（用于返回错误信息）
     * @param handler  目标处理器（接口方法）
     * @return true：令牌合法，继续执行；false：令牌非法，终止请求
     * @throws Exception 处理过程中的异常
     */
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 1. 设置响应格式：确保前端能正确解析错误信息（JSON格式）
        response.setContentType("application/json;charset=UTF-8");
        response.setCharacterEncoding("UTF-8");

        // 2. 从请求头中获取JWT令牌（通常放在 Authorization 头中，格式：Bearer <token>）
        String authHeader = request.getHeader("Authorization");

        // 3. 第一步验证：Authorization头是否存在且格式正确（以"Bearer "开头）
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            response.getWriter().write("{\"code\":401,\"message\":\"未携带令牌或令牌格式错误（需以Bearer 开头）\"}");
            // 终止请求，不进入后续接口
            return false;
        }

        // 4. 提取纯令牌（去掉"Bearer "前缀，截取第7位及以后的字符）
        String token = authHeader.substring(7);

        try {
            // 5. 调用JwtUtil验证令牌合法性（底层会校验签名、过期时间）
            boolean isTokenValid = jwtUtil.validateToken(token);
            if (!isTokenValid) {
                response.getWriter().write("{\"code\":401,\"message\":\"令牌无效\"}");
                return false;
            }

            // 6. 令牌合法：可进一步解析用户名，存入request属性（供后续接口使用，如获取当前登录用户）
            String username = jwtUtil.getUsernameFromToken(token);
            // 存入request，接口中可通过request.getAttribute获取
            request.setAttribute("currentUsername", username);

            // 7. 令牌验证通过，继续执行后续接口
            return true;

        } catch (ExpiredJwtException e) {
            // 令牌过期异常
            response.getWriter().write("{\"code\":401,\"message\":\"令牌已过期，请重新登录\"}");
            return false;
        } catch (MalformedJwtException e) {
            // 令牌格式错误（如非法字符、结构异常）
            response.getWriter().write("{\"code\":401,\"message\":\"令牌格式错误\"}");
            return false;
        } catch (SignatureException e) {
            // 令牌签名错误（如secretKey不匹配、令牌被篡改）
            response.getWriter().write("{\"code\":401,\"message\":\"令牌签名无效（可能被篡改）\"}");
            return false;
        } catch (UnsupportedJwtException e) {
            // 不支持的JWT格式（如算法不匹配）
            response.getWriter().write("{\"code\":401,\"message\":\"不支持的令牌格式\"}");
            return false;
        } catch (Exception e) {
            // 其他未知异常
            response.getWriter().write("{\"code\":500,\"message\":\"令牌验证过程异常：" + e.getMessage() + "\"}");
            return false;
        }
    }
}