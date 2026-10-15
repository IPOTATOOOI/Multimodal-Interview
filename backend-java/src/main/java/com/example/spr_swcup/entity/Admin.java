package com.example.spr_swcup.entity;

import lombok.Data;

import java.util.Date;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-09-11
 */
@Data
public class Admin {
    private Integer id;
    private String username;
    private String password;
    private String email;
    private Date createTime;
    private Integer status;
    private String faceFilename;
}