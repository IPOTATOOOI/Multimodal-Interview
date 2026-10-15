package com.example.spr_swcup.mapper.positionInfo;

import com.example.spr_swcup.entity.Domain;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Mapper
public interface DomainMapper {
    List<Domain> findAll();
    Domain findByDomainName(String domainName);
}