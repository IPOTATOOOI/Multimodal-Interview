package com.example.spr_swcup.service;
/*
JWT 令牌服务，负责令牌的生成和验证。
生成新 JWT 令牌 (generateToken())
验证现有令牌的合法性 (validateToken())
解析令牌获取用户信息
处理令牌的加密签名
管理令牌有效期
* */
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.util.Date;
import java.security.Key;

@Service
public class JwtTokenService {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration-minutes}")
    private int expirationMinutes;

    private Key getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes());
    }

    public String generateToken(String username) {
        Date now = new Date();
        Date expiration = new Date(now.getTime() + expirationMinutes * 60 * 1000L);

        return Jwts.builder()
                .setSubject(username)
                .setIssuedAt(now)
                .setExpiration(expiration)
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    // 添加这个方法来解决"无法解析方法"的问题
    public String validateToken(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token)
                    .getBody();

            return claims.getSubject();
        } catch (JwtException | IllegalArgumentException e) {
            throw new InvalidJwtException("无法验证凭证");
        }
    }

    // 自定义异常类
    public static class InvalidJwtException extends RuntimeException {
        public InvalidJwtException(String message) {
            super(message);
        }
    }
}