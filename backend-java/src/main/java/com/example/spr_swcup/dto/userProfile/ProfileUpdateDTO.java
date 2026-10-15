package com.example.spr_swcup.dto.userProfile;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.*;
import lombok.Data;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
@Schema(description = "用户资料更新请求")
public class ProfileUpdateDTO {
    @NotBlank(message = "用户名不能为空")
    private String username;

    private String name;

    @Pattern(regexp = "^(男|女|未知)$", message = "性别必须是'男'、'女'或'未知'")
    private String gender;
    
    private Integer age;

    private String university;
    private String major;
}