package com.example.spr_swcup.service.history;

import com.example.spr_swcup.dto.history.QADTO;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class AudioFileService {
    
    private static final String AUDIO_DIR = "src/main/resources/uploads/audio";
    
    /**
     * 为qa_log匹配录音文件
     */
    public List<QADTO> matchAudioFilesToQALog(Integer historyId, List<QADTO> qaList) {
        if (qaList == null || qaList.isEmpty()) {
            return qaList;
        }
        for (int i = 0; i < qaList.size(); i++) {
            QADTO qa = qaList.get(i);
            // 顺序号，从2开始
            int number = i + 2;
            // 直接拼接文件名，不判断文件是否存在
            String audioFileName = "audio/his-" + historyId + "-audioid-" + number + ".wav";
            qa.setAudioFile(audioFileName);
        }
        return qaList;
    }

    /**
     * 查找录音文件（按顺序号）
     */
    private String findAudioFileByNumber(Integer historyId, int number) {
        String[] possiblePatterns = {
            "his-" + historyId + "-audioid-" + number + ".wav",
            "his-" + historyId + "-audioid-" + number + ".mp3"
        };
        
        File audioDir = new File(AUDIO_DIR);
        if (!audioDir.exists()) {
            log.warn("音频目录不存在: {}", AUDIO_DIR);
            return null;
        }
        
        for (String pattern : possiblePatterns) {
            File audioFile = new File(audioDir, pattern);
            if (audioFile.exists()) {
                log.info("找到录音文件: {}", pattern);
                return "audio/" + pattern;
            }
        }
        
        log.warn("未找到录音文件: historyId={}, number={}", historyId, number);
        return null;
    }
    
    /**
     * 过滤qa_log，跳过首个回答
     */
    public List<QADTO> filterQALogSkipFirstAnswer(List<QADTO> qaList) {
        if (qaList == null || qaList.isEmpty()) {
            return qaList;
        }
        
        // 如果第一个是回答（role=1），则跳过
        if (qaList.get(0).getRole() == 1) {
            log.info("跳过首个回答，原始qa数量: {}, 过滤后数量: {}", qaList.size(), qaList.size() - 1);
            // 创建新的ArrayList而不是使用subList以避免序列化问题
            return new ArrayList<>(qaList.subList(1, qaList.size()));
        }
        
        return qaList;
    }
} 