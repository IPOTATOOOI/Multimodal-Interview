package com.example.spr_swcup.service;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.userProfile.ProfileUpdateDTO;
import com.example.spr_swcup.dto.userProfile.UserProfileDTO;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
public interface UserService {
    Result<?> updateProfile(ProfileUpdateDTO dto);

    Result<UserProfileDTO> getUserProfile(String username, boolean isAdmin);
}