package com.example.spr_swcup.service.history;

import com.example.spr_swcup.dto.history.UserHistoryResponse;
import com.example.spr_swcup.dto.history.DetailedHistoryResponse;

public interface HistoryService {
    /**
     * 获取用户的所有面试历史记录（简要信息）
     * @param userId 用户ID
     * @return 用户历史记录响应
     */
    UserHistoryResponse getUserHistory(String userId);

    /**
     * 获取指定的面试历史记录及其所有问答
     * @param historyId 历史记录ID
     * @return 详细历史记录响应
     */
    DetailedHistoryResponse getHistoryDetail(Integer historyId);
}