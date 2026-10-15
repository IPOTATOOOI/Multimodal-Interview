package com.example.spr_swcup.mapper.history;

import com.example.spr_swcup.dto.history.BasicHistoryDTO;
import com.example.spr_swcup.dto.history.DetailedHistoryDTO;
import com.example.spr_swcup.dto.history.ImportHistoryDTO;
import com.example.spr_swcup.dto.history.QADTO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface HistoryMapper {
    /**
     * 获取用户的所有面试历史记录（简要信息）
     * @param userId 用户ID
     * @return 历史记录列表
     */
    List<BasicHistoryDTO> getUserInterviewHistory(@Param("userId") String userId);
    
    /**
     * 获取指定的面试历史记录详细信息
     * @param historyId 历史记录ID
     * @return 详细历史记录
     */
    DetailedHistoryDTO getInterviewHistoryById(@Param("historyId") Integer historyId);
    
    /**
     * 插入一条面试历史记录
     * @param historyDTO 面试历史记录DTO
     * @return 插入记录数
     */
    int insertInterviewHistory(ImportHistoryDTO historyDTO);
}