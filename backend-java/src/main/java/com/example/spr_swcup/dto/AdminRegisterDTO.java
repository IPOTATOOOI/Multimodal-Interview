package com.example.spr_swcup.dto;

import lombok.Data;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-09-11
 */
@Data
public class AdminRegisterDTO {
    /**
     * 用户名
     */
    private String username;

    /**
     * 密码
     */
    private String password;

    /**
     * 邮箱
     */
    private String email;
}
