package com.example.spr_swcup.mapper.user;

import com.example.spr_swcup.entity.Admin;
import org.apache.ibatis.annotations.Mapper;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-09-11
 */
@Mapper
public interface AdminMapper {
    Admin findByUsername(String username);
    int insert(Admin admin);
    Admin findById(Integer id);
}