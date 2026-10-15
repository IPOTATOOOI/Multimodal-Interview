package com.example.spr_swcup.config;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.util.Date;
import javax.crypto.SecretKey;

@Component
public class JwtUtil {
    private final SecretKey secretKey;

    public JwtUtil(@Value("${jwt.secret}") String base64Key) {
        // 将Base64编码的密钥转换为SecretKey
        this.secretKey = Keys.hmacShaKeyFor(java.util.Base64.getDecoder().decode(base64Key));
    }

    @Value("${jwt.expiration-minutes}")
    private long expirationMinutes;

    public String generateToken(String username) {
        long expirationTimeMillis = expirationMinutes * 60 * 1000;
        return Jwts.builder()
                .setSubject(username)
                .setExpiration(new Date(System.currentTimeMillis() + expirationTimeMillis))
                // 使用SecretKey
                .signWith(secretKey, SignatureAlgorithm.HS512)
                .compact();
    }

    // getUsernameFromToken和validateToken方法也需要做相应修改
    public String getUsernameFromToken(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(secretKey)
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }

    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}