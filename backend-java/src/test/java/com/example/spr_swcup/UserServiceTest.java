package com.example.spr_swcup;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.userProfile.ProfileUpdateDTO;
import com.example.spr_swcup.dto.userProfile.UserProfileDTO;
import com.example.spr_swcup.mapper.user.UserMapper;
import com.example.spr_swcup.mapper.user.AdminUserMapper;
import com.example.spr_swcup.service.UserService;
import com.example.spr_swcup.service.Impl.UserServiceImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

public class UserServiceTest {
    @Mock
    private UserMapper userMapper;
    
    @Mock
    private AdminUserMapper adminUserMapper;

    @InjectMocks
    private UserServiceImpl userService;

    @BeforeEach
    public void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void contextLoads() {
        assertNotNull(userService);
    }

    @Test
    public void testUpdateProfileSuccess() {
        when(userMapper.updateProfileByUsername(any(ProfileUpdateDTO.class))).thenReturn(1);

        ProfileUpdateDTO dto = new ProfileUpdateDTO();
        dto.setUsername("testuser");
        dto.setName("Test User");
        dto.setGender("女");
        dto.setAge(25);
        dto.setUniversity("UPC");
        dto.setMajor("SW");

        Result<?> result = userService.updateProfile(dto);

        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals("资料更新成功", result.getMessage());

        verify(userMapper, times(1)).updateProfileByUsername(any(ProfileUpdateDTO.class));
    }

    @Test
    public void testUpdateProfileUserNotFound() {
        when(userMapper.updateProfileByUsername(any(ProfileUpdateDTO.class))).thenReturn(0);

        ProfileUpdateDTO dto = new ProfileUpdateDTO();
        dto.setUsername("nonexistentuser");
        dto.setName("Test User");
        dto.setGender("女");
        dto.setAge(25);
        dto.setUniversity("UPC");
        dto.setMajor("SW");

        Result<?> result = userService.updateProfile(dto);

        assertNotNull(result);
        assertEquals(404, result.getCode());
        assertEquals("用户名 'nonexistentuser' 不存在", result.getMessage());

        verify(userMapper, times(1)).updateProfileByUsername(any(ProfileUpdateDTO.class));
    }
    
    @Test
    public void testUpdateProfileWithNullDto() {
        Result<?> result = userService.updateProfile(null);
        
        assertNotNull(result);
        assertEquals(400, result.getCode());
        assertEquals("参数不能为空", result.getMessage());
        
        verify(userMapper, never()).updateProfileByUsername(any());
    }
    
    @Test
    public void testGetUserProfileForNormalUser() {
        UserProfileDTO profile = new UserProfileDTO();
        profile.setName("Test User");
        
        when(userMapper.selectProfileByUsername("testuser")).thenReturn(profile);
        
        Result<UserProfileDTO> result = userService.getUserProfile("testuser", false);
        
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals(profile, result.getData());
        
        verify(userMapper, times(1)).selectProfileByUsername("testuser");
        verify(adminUserMapper, never()).selectAdminProfileByUsername(anyString());
    }
    
    @Test
    public void testGetUserProfileForAdminUser() {
        UserProfileDTO profile = new UserProfileDTO();
        profile.setName("Admin User");
        
        when(adminUserMapper.selectAdminProfileByUsername("admin")).thenReturn(profile);
        
        Result<UserProfileDTO> result = userService.getUserProfile("admin", true);
        
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals(profile, result.getData());
        
        verify(adminUserMapper, times(1)).selectAdminProfileByUsername("admin");
        verify(userMapper, never()).selectProfileByUsername(anyString());
    }
    
    @Test
    public void testGetUserProfileNotFound() {
        when(userMapper.selectProfileByUsername("nonexistent")).thenReturn(null);
        
        Result<UserProfileDTO> result = userService.getUserProfile("nonexistent", false);
        
        assertNotNull(result);
        assertEquals(404, result.getCode());
        assertEquals("用户名 'nonexistent' 不存在", result.getMessage());
        assertNull(result.getData());
        
        verify(userMapper, times(1)).selectProfileByUsername("nonexistent");
    }
}