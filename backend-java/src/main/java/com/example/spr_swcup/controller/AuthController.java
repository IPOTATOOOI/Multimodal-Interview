package com.example.spr_swcup.controller;

import com.example.spr_swcup.dto.UserLoginRequest;
import com.example.spr_swcup.dto.UserRegistrationRequest;
import com.example.spr_swcup.dto.UserResponse;
import com.example.spr_swcup.model.User;
import com.example.spr_swcup.service.AuthService;
import com.example.spr_swcup.service.JwtTokenService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
public class AuthController {

    @Autowired
    private AuthService authService;

    @Autowired
    private JwtTokenService jwtTokenService;

    @PostMapping("/register")
    public ResponseEntity<String> register(@RequestBody UserRegistrationRequest request) {
        authService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body("用户注册成功");
    }

    @PostMapping("/login")
    public ResponseEntity<TokenResponse> login(@RequestBody UserLoginRequest request) {
        User user = authService.authenticate(request);
        String token = jwtTokenService.generateToken(user.getUsername());
        return ResponseEntity.ok(new TokenResponse(token, "bearer", user.getUserId().toString()));
    }

    @GetMapping("/me")
    public ResponseEntity<UserResponse> getCurrentUser(Authentication authentication) {
        String username = authentication.getName();
        // 实际应用中需要从数据库获取完整用户信息
        UserResponse response = new UserResponse();
        response.setUsername(username);
        return ResponseEntity.ok(response);
    }

    private static class TokenResponse {
        private String access_token;
        private String token_type = "bearer";
        private String user_id;

        public TokenResponse(String access_token, String token_type, String user_id) {
            this.access_token = access_token;
            this.token_type = token_type;
            this.user_id = user_id;
        }

        // Getters
        public String getAccess_token() { return access_token; }
        public String getToken_type() { return token_type; }
        public String getUser_id() { return user_id; }
    }
}
