package com.example.spr_swcup.entity;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Date;
/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
@Schema(name = "用户信息")
public class User {
    private Integer userId;
    private String username;
    private String name;
    // 1-男, 2-女, 0-未知
    private Integer gender;
    private Integer age;
    private String password;
    private Date createdAt;
    private Date updatedAt;
    private String email;
    private String university;
    private String major;
}
