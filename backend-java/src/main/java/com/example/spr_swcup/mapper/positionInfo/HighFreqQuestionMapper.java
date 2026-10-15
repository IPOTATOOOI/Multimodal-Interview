package com.example.spr_swcup.mapper.positionInfo;

import com.example.spr_swcup.entity.HighFreqQuestion;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Mapper
public interface HighFreqQuestionMapper {
    List<HighFreqQuestion> findByPositionId(Long positionId);
}