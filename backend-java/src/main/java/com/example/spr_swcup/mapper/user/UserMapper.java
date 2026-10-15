package com.example.spr_swcup.mapper.user;
import com.example.spr_swcup.dto.userProfile.ProfileUpdateDTO;
import com.example.spr_swcup.dto.userProfile.UserProfileDTO;
import org.apache.ibatis.annotations.Mapper;
/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Mapper
public interface UserMapper {
    int updateProfileByUsername(ProfileUpdateDTO dto);
    UserProfileDTO selectProfileByUsername(String username);
}
