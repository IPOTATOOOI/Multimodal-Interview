package com.example.spr_swcup.controller;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.AdminLoginDTO;
import com.example.spr_swcup.entity.Admin;
import com.example.spr_swcup.service.AdminService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-09-11
 */
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
@RestController
@RequestMapping("/api/admin")
public class AdminController {
    @Autowired
    private AdminService adminService;

    @PostMapping("/login")
    public Result<String> login(@RequestBody AdminLoginDTO loginDTO) {
        String token = adminService.login(loginDTO.getUsername(), loginDTO.getPassword());
        return Result.success(token);
    }

    @PostMapping("/register")
    public Result<Admin> register(@RequestBody Admin admin) {
        return Result.success(adminService.register(admin));
    }
}
