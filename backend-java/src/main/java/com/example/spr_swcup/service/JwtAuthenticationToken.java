package com.example.spr_swcup.service;
/*
封装 JWT 认证信息的专用令牌对象。
存储已验证用户的主体（用户名）
包含原始令牌凭证
向 Spring Security 提供认证信息
标记为已验证状态（setAuthenticated(true)）
*/
import org.springframework.security.authentication.AbstractAuthenticationToken;
import java.util.Collections;

public class JwtAuthenticationToken extends AbstractAuthenticationToken {

    private final String principal;
    private final String credentials;

    public JwtAuthenticationToken(String username, String token) {
        super(Collections.emptyList());
        this.principal = username;
        this.credentials = token;
        // 更新为调用父类方法
        super.setAuthenticated(true);
    }

    @Override
    public String getCredentials() {
        return this.credentials;
    }

    @Override
    public String getPrincipal() {
        return this.principal;
    }
}