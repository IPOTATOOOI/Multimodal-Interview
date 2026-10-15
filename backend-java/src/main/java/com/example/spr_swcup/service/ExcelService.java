package com.example.spr_swcup.service;

import com.example.spr_swcup.dto.history.UserHistoryResponse;

import jakarta.servlet.http.HttpServletResponse;

public interface ExcelService {
    /**
     * 导出用户面试历史到Excel
     */
    void exportUserHistoryToExcel(UserHistoryResponse userHistoryResponse, HttpServletResponse response);

    /**
     * 从Excel导入用户面试历史
     */
    int importUserHistoryFromExcel(String filePath);
}