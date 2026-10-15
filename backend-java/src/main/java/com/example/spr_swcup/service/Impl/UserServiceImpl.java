package com.example.spr_swcup.service.Impl;
import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.userProfile.ProfileUpdateDTO;
import com.example.spr_swcup.dto.userProfile.UserProfileDTO;
import com.example.spr_swcup.mapper.user.UserMapper;
import com.example.spr_swcup.mapper.user.AdminUserMapper;
import com.example.spr_swcup.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {
    private final UserMapper userMapper;
    private final AdminUserMapper adminUserMapper;

    @Transactional
    @Override
    public Result<?> updateProfile(ProfileUpdateDTO dto) {
        if (dto == null){
            return Result.fail(400, "参数不能为空");
        }
        int affectedRows = userMapper.updateProfileByUsername(dto);
        if (affectedRows == 0) {
            return Result.fail(404, "用户名 '" + dto.getUsername() + "' 不存在");
        }
        return Result.success("资料更新成功");
    }


    @Override
    public Result<UserProfileDTO> getUserProfile(String username, boolean isAdmin) {
        UserProfileDTO profile = null;
        
        if (isAdmin) {
            profile = adminUserMapper.selectAdminProfileByUsername(username);
        } else {
            profile = userMapper.selectProfileByUsername(username);
        }
        
        if (profile == null) {
            return Result.fail(404, "用户名 '" + username + "' 不存在");
        }
        return Result.success(profile);
    }
}