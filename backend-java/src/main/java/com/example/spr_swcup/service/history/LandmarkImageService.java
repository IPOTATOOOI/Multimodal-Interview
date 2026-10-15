package com.example.spr_swcup.service.history;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

@Slf4j
@Service
public class LandmarkImageService {
    
    private static final String LANDMARK_DIR = "src/main/resources/uploads/facialLandmarks";
    
    /**
     * 获取前三张landmark截图
     * @param historyId 历史记录ID
     * @return landmark截图列表
     */
    public List<String> getLandmarkImages(Integer historyId) {
        // 当前为固定示例图片，实际可按history_id动态获取
//        List<String> landmarkImages = Arrays.asList(
//            "example_07_landmarks.jpg",
//            "example_08_landmarks.jpg",
//            "example_010_landmarks.jpg"
//        );
        
        //如需根据history_id动态获取截图，可使用如下代码：
        // return getLandmarkImagesByHistoryId(historyId);
        
        //return landmarkImages;
        // 直接拼接返回3个图片文件名，不判断文件是否存在
        List<String> landmarkImages = new ArrayList<>();
        for (int n = 1; n <= 3; n++) {
            String filename = String.format("his-%d-img-%d_landmarks.jpg", historyId, n);
            landmarkImages.add(filename);
        }
        return landmarkImages;
    }
    
    /**
     * 根据history_id动态获取landmark截图
     */
    public List<String> getLandmarkImagesByHistoryId(Integer historyId) {
        List<String> landmarkImages = new ArrayList<>();
        
        try {
            File landmarkDir = new File(LANDMARK_DIR);
            if (!landmarkDir.exists()) {
                log.warn("Landmark目录不存在: {}", LANDMARK_DIR);
                return landmarkImages;
            }
            
            // 查找对应的landmark截图文件
            for (int n = 1; n <= 3; n++) {
                String filename = String.format("his-%d-img-%d_landmarks.jpg", historyId, n);
                File file = new File(landmarkDir, filename);
                if (file.exists()) {
                    landmarkImages.add(filename);
                    log.info("找到landmark截图: {}", filename);
                } else {
                    log.debug("未找到landmark截图: {}", filename);
                }
            }
            
        } catch (Exception e) {
            log.error("获取landmark截图失败: {}", e.getMessage());
        }
        
        return landmarkImages;
    }
} 