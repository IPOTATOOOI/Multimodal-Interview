package com.example.spr_swcup.controller;
import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.userProfile.ProfileUpdateDTO;
import com.example.spr_swcup.dto.userProfile.UserProfileDTO;
import com.example.spr_swcup.service.UserService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
public class UserController {
    private final UserService userService;
    @PutMapping("/update-profile")
    public Result<?> updateProfile(@Valid @RequestBody ProfileUpdateDTO dto) {
        if (dto == null)
            return Result.error(400, "参数不能为空");
        return userService.updateProfile(dto);
    }

    @GetMapping("/user-profile/{username}")
    public Result<UserProfileDTO> getUserProfile(
            @PathVariable
            @NotBlank(message = "用户名不能为空")
            String username,
            @RequestParam(defaultValue = "false")
            boolean isAdmin) {
        return userService.getUserProfile(username, isAdmin);
    }
}
