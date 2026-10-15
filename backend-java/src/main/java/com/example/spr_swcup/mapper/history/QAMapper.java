package com.example.spr_swcup.mapper.history;

import com.example.spr_swcup.dto.history.QADTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface QAMapper {
    /**
     * 根据历史记录ID获取所有问答记录
     * @param historyId 历史记录ID
     * @return 问答记录列表
     */
    List<QADTO> getQAByHistoryId(@Param("historyId") Integer historyId);
} 