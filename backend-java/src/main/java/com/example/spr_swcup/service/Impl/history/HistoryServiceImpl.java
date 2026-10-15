package com.example.spr_swcup.service.Impl.history;

import com.example.spr_swcup.dto.history.BasicHistoryDTO;
import com.example.spr_swcup.dto.history.UserHistoryResponse;
import com.example.spr_swcup.dto.history.DetailedHistoryDTO;
import com.example.spr_swcup.dto.history.DetailedHistoryResponse;
import com.example.spr_swcup.dto.history.QADTO;
import com.example.spr_swcup.mapper.history.HistoryMapper;
import com.example.spr_swcup.mapper.history.QAMapper;
import com.example.spr_swcup.service.history.HistoryService;
import com.example.spr_swcup.service.history.AudioFileService;
import com.example.spr_swcup.service.history.LandmarkImageService;
import com.example.spr_swcup.service.history.HistoryNotFoundException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
public class HistoryServiceImpl implements HistoryService {
    
    @Autowired
    private HistoryMapper historyMapper;
    
    @Autowired
    private QAMapper qaMapper;
    
    @Autowired
    private AudioFileService audioFileService;
    
    @Autowired
    private LandmarkImageService landmarkImageService;
    
    @Override
    public UserHistoryResponse getUserHistory(String userId) {
        try {
            log.info("获取用户面试历史记录: user_id={}", userId);
            List<BasicHistoryDTO> historyList = historyMapper.getUserInterviewHistory(userId);
            log.info("获取用户面试历史记录成功: user_id={}, count={}", userId, historyList.size());
            
            UserHistoryResponse response = new UserHistoryResponse();
            response.setUserId(userId);
            response.setTotal(historyList.size());
            response.setHistoryList(historyList);
            
            return response;
        } catch (Exception e) {
            String errorMsg = "获取用户面试历史记录失败: " + e.getMessage();
            log.error(errorMsg, e);
            throw new RuntimeException(errorMsg);
        }
    }
    
    @Override
    public DetailedHistoryResponse getHistoryDetail(Integer historyId) {
        try {
            log.info("获取面试历史记录: history_id={}", historyId);
            
            // 查询历史记录
            DetailedHistoryDTO history = historyMapper.getInterviewHistoryById(historyId);
            if (history == null) {
                log.info("未找到面试历史记录: {}", historyId);
                throw new HistoryNotFoundException("历史记录不存在");
            }
            
            // 查询该历史下所有qa
            List<QADTO> qaList = qaMapper.getQAByHistoryId(historyId);
            
            // 为qa_log添加录音文件信息
            try {
                qaList = audioFileService.filterQALogSkipFirstAnswer(qaList);
                qaList = audioFileService.matchAudioFilesToQALog(historyId, qaList);
                log.info("已为history_id={}的qa_log过滤首个回答并添加录音文件信息", historyId);
            } catch (Exception e) {
                log.error("为qa_log添加录音文件信息失败: {}", e.getMessage());
                // 即使录音文件匹配失败，也不影响主要功能
            }
            
            // 获取前三张landmark截图
            log.info("获取history_id={}的landmark图片", historyId);
            List<String> landmarkImages = landmarkImageService.getLandmarkImages(historyId);
            log.info("获取history_id={}的landmark图片成功: count={}", historyId, landmarkImages.size());
            
            DetailedHistoryResponse response = new DetailedHistoryResponse();
            response.setInterviewHistory(history);
            response.setQaLog(qaList);
            response.setLandmarkImages(landmarkImages);
            
            log.info("获取面试历史及qa成功: history_id={}", historyId);
            return response;
            
        } catch (HistoryNotFoundException e) {
            throw e;
        } catch (Exception e) {
            String errorMsg = "获取面试历史记录失败: " + e.getMessage();
            log.error(errorMsg, e);
            throw new RuntimeException(errorMsg);
        }
    }
    

}
