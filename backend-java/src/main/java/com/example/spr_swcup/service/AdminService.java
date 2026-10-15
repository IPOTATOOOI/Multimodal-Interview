package com.example.spr_swcup.service;

import com.example.spr_swcup.config.JwtUtil;
import com.example.spr_swcup.entity.Admin;
import com.example.spr_swcup.mapper.user.AdminMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCrypt;
import org.springframework.stereotype.Service;

import java.util.Date;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-09-11
 */
@Service
public class AdminService {
    @Autowired
    private AdminMapper adminMapper;
    @Autowired
    private JwtUtil jwtUtil;

    public Admin register(Admin admin) {
        // 检查用户名是否存在
        if (adminMapper.findByUsername(admin.getUsername()) != null) {
            throw new RuntimeException("用户名已存在");
        }

        // 密码加密
        admin.setPassword(BCrypt.hashpw(admin.getPassword(), BCrypt.gensalt()));
        admin.setCreateTime(new Date());
        admin.setStatus(1);

        adminMapper.insert(admin);
        return admin;
    }

    public String login(String username, String password) {
        Admin admin = adminMapper.findByUsername(username);
        if (admin == null) {
            throw new RuntimeException("用户不存在");
        }

        if (!BCrypt.checkpw(password, admin.getPassword())) {
            throw new RuntimeException("密码错误");
        }

        return jwtUtil.generateToken(username);
    }
}
