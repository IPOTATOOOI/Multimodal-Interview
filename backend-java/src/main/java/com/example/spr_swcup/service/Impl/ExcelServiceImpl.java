package com.example.spr_swcup.service.Impl;

import com.alibaba.excel.EasyExcel;
import com.example.spr_swcup.dto.excel.UserHistoryExcelDTO;
import com.example.spr_swcup.dto.history.BasicHistoryDTO;
import com.example.spr_swcup.dto.history.ImportHistoryDTO;
import com.example.spr_swcup.dto.history.UserHistoryResponse;
import com.example.spr_swcup.mapper.history.HistoryMapper;
import com.example.spr_swcup.service.ExcelService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.net.URLEncoder;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.UUID;

@Service
public class ExcelServiceImpl implements ExcelService {

    @Autowired
    private HistoryMapper historyMapper;

    @Override
    public void exportUserHistoryToExcel(UserHistoryResponse userHistoryResponse, HttpServletResponse response) {
        try {
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setCharacterEncoding("utf-8");
            String fileName = URLEncoder.encode("用户面试历史记录", "UTF-8").replaceAll("\\+", "%20");
            response.setHeader("Content-disposition", "attachment;filename*=utf-8''" + fileName + ".xlsx");

            // 转换业务模型为ExcelDTO
            List<UserHistoryExcelDTO> excelDTOList = convertToExcelDTOList(userHistoryResponse);

            // 写入Excel到响应流
            EasyExcel.write(response.getOutputStream(), UserHistoryExcelDTO.class)
                    .sheet("面试历史记录")
                    .doWrite(excelDTOList);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // 业务模型 -> ExcelDTO 转换
    private List<UserHistoryExcelDTO> convertToExcelDTOList(UserHistoryResponse userHistoryResponse) {
        List<UserHistoryExcelDTO> result = new ArrayList<>();
        if (userHistoryResponse.getHistoryList() != null) {
            for (BasicHistoryDTO historyDTO : userHistoryResponse.getHistoryList()) {
                UserHistoryExcelDTO excelDTO = new UserHistoryExcelDTO();
                // 将Integer类型转换为Long类型
                excelDTO.setHistoryId(historyDTO.getHistoryId().longValue());
                excelDTO.setInterviewTime(historyDTO.getInterviewTime());
                excelDTO.setField(historyDTO.getField());
                excelDTO.setPosition(historyDTO.getPosition());
                excelDTO.setProfessionalKnowledge(historyDTO.getProfessionalKnowledge());
                excelDTO.setSkillMatch(historyDTO.getSkillMatch());
                excelDTO.setLanguageExpression(historyDTO.getLanguageExpression());
                excelDTO.setLogicalThinking(historyDTO.getLogicalThinking());
                excelDTO.setInnovationAbility(historyDTO.getInnovationAbility());
                excelDTO.setStressResistance(historyDTO.getStressResistance());
                excelDTO.setFeedbackSuggestion1(historyDTO.getFeedbackSuggestion1());
                excelDTO.setScore(historyDTO.getScore());
                excelDTO.setEndTime(historyDTO.getEndTime());
                result.add(excelDTO);
            }
        }
        return result;
    }

    @Override
    public int importUserHistoryFromExcel(String filePath) {
        try {
            // 从Excel读取数据
            List<UserHistoryExcelDTO> excelDTOList = EasyExcel.read(filePath)
                    .head(UserHistoryExcelDTO.class)
                    .sheet()
                    .doReadSync();

            // 将excelDTOList转换为entity并保存到数据库
            int count = 0;
            for (UserHistoryExcelDTO excelDTO : excelDTOList) {
                ImportHistoryDTO historyDTO = new ImportHistoryDTO();
                historyDTO.setHistoryId(excelDTO.getHistoryId().intValue());
                historyDTO.setInterviewTime(excelDTO.getInterviewTime());
                historyDTO.setField(excelDTO.getField());
                historyDTO.setPosition(excelDTO.getPosition());
                historyDTO.setProfessionalKnowledge(excelDTO.getProfessionalKnowledge());
                historyDTO.setSkillMatch(excelDTO.getSkillMatch());
                historyDTO.setLanguageExpression(excelDTO.getLanguageExpression());
                historyDTO.setLogicalThinking(excelDTO.getLogicalThinking());
                historyDTO.setInnovationAbility(excelDTO.getInnovationAbility());
                historyDTO.setStressResistance(excelDTO.getStressResistance());
                historyDTO.setFeedbackSuggestion1(excelDTO.getFeedbackSuggestion1());
                historyDTO.setScore(excelDTO.getScore());
                historyDTO.setEndTime(excelDTO.getEndTime());
                // 设置创建时间
                historyDTO.setCreatedAt(new Date());

                // 设置用户ID为默认值1，因为在Excel导入中没有用户ID字段
                // 在实际应用中，你可能需要通过其他方式获取用户ID
                // 使用默认用户ID 1
                historyDTO.setUserId(1);

                // 插入到数据库
                historyMapper.insertInterviewHistory(historyDTO);
                count++;
            }

            return count;
        } catch (Exception e) {
            throw new RuntimeException("导入Excel数据失败: " + e.getMessage(), e);
        }
    }
}