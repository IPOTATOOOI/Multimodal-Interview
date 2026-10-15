package com.example.spr_swcup.mapper.user;

import com.example.spr_swcup.dto.userProfile.UserProfileDTO;
import org.apache.ibatis.annotations.Mapper;

/**
 * 管理员用户Mapper接口
 */
@Mapper
public interface AdminUserMapper {
    /**
     * 根据用户名查询管理员资料
     * @param username 用户名
     * @return 用户资料DTO
     */
    UserProfileDTO selectAdminProfileByUsername(String username);
}