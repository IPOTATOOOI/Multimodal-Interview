package com.example.spr_swcup.dto.userProfile;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
@Schema(description = "用户资料响应")
public class UserProfileDTO {
    private String name;
    private String gender;
    private Integer age;
    private String university;
    private String major;
}
