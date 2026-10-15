package com.example.spr_swcup.service;
/*
 * 创建一个过滤器，继承OncePerRequestFilter类，并实现doFilterInternal方法
 * 请求过滤器，用于处理 JWT 认证。
 * 拦截所有传入的 HTTP 请求
检查请求头中的 Authorization字段
提取并验证 Bearer Token
验证成功后设置 Spring Security 上下文
处理认证失败（返回 401 或 500 错误）
确保合法请求继续处理链
 */
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;

@Component
public class JwtTokenFilter extends OncePerRequestFilter {

    @Autowired
    private JwtTokenService jwtTokenService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain filterChain)
            throws ServletException, IOException {

        String header = request.getHeader("Authorization");

        if (header != null && header.startsWith("Bearer ")) {
            String token = header.substring(7);
            try {
                String username = jwtTokenService.validateToken(token);
                if (username != null) {
                    SecurityContextHolder.getContext().setAuthentication(
                            new JwtAuthenticationToken(username, token)
                    );
                }
            } catch (JwtTokenService.InvalidJwtException e) {
                // 使用自定义异常处理
                response.sendError(HttpServletResponse.SC_UNAUTHORIZED, e.getMessage());
                return;
            } catch (Exception e) {
                // 处理其他异常
                response.sendError(HttpServletResponse.SC_INTERNAL_SERVER_ERROR, "服务器内部错误");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }
}