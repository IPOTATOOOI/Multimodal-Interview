package com.example.spr_swcup.mapper.positionInfo;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import com.example.spr_swcup.entity.Position;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Mapper
public interface PositionMapper {
    Position findByPositionNameAndDomainId(
            @Param("positionName") String positionName,
            @Param("domainId") Integer domainId
    );
}
