package com.example.spr_swcup.rmi;

import com.alibaba.excel.EasyExcel;
import com.example.spr_swcup.dto.excel.UserHistoryExcelDTO;
import com.example.spr_swcup.dto.history.BasicHistoryDTO;
import com.example.spr_swcup.dto.history.UserHistoryResponse;

import java.io.ByteArrayOutputStream;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.ArrayList;
import java.util.List;

/**
 * 远程Excel导出服务实现类
 * 负责实际生成Excel文件并返回字节流
 */
public class ExcelExportRemoteServiceImpl extends UnicastRemoteObject implements ExcelExportRemoteService {

    protected ExcelExportRemoteServiceImpl() throws RemoteException {
        super();
    }

    @Override
    public byte[] generateHistoryExcel(UserHistoryResponse userHistory) throws RemoteException {
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            List<UserHistoryExcelDTO> excelDTOList = convertToExcelDTO(userHistory);

            EasyExcel.write(out, UserHistoryExcelDTO.class)
                    .sheet("面试历史记录")
                    .doWrite(excelDTOList);

            return out.toByteArray();
        } catch (Exception e) {
            throw new RemoteException("远程生成Excel失败：" + e.getMessage());
        }
    }

    private List<UserHistoryExcelDTO> convertToExcelDTO(UserHistoryResponse userHistory) {
        List<UserHistoryExcelDTO> result = new ArrayList<>();
        if (userHistory.getHistoryList() != null) {
            for (BasicHistoryDTO history : userHistory.getHistoryList()) {
                UserHistoryExcelDTO dto = new UserHistoryExcelDTO();
                dto.setHistoryId(history.getHistoryId().longValue());
                dto.setInterviewTime(history.getInterviewTime());
                dto.setField(history.getField());
                dto.setPosition(history.getPosition());
                dto.setProfessionalKnowledge(history.getProfessionalKnowledge());
                // 其他字段映射...
                result.add(dto);
            }
        }
        return result;
    }
}