package com.example.spr_swcup.controller.history;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.history.UserHistoryResponse;
import com.example.spr_swcup.dto.history.DetailedHistoryResponse;
import com.example.spr_swcup.service.history.HistoryService;
import com.example.spr_swcup.service.history.HistoryNotFoundException;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.example.spr_swcup.service.ExcelService;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

@Slf4j
@RestController
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
@RequestMapping("/history")
public class HistoryController {
    
    @Autowired
    private HistoryService historyService;

    @Autowired
    private ExcelService excelService;

    @GetMapping("/user/{user_id}")
    public Result<UserHistoryResponse> getUserHistory(@PathVariable("user_id") String userId) {
        try {
            log.info("获取用户面试历史记录: user_id={}", userId);
            UserHistoryResponse response = historyService.getUserHistory(userId);
            log.info("获取用户面试历史记录成功: user_id={}, count={}", userId, response.getTotal());
            log.info("获取用户面试历史记录成功: user_id={}, count={}", userId, response);
            return Result.success(response);
        } catch (Exception e) {
            String errorMsg = "获取用户面试历史记录失败: " + e.getMessage();
            log.error(errorMsg, e);
            return Result.error(500, errorMsg);
        }
    }
    
    @GetMapping("/{history_id}")
    public Result<DetailedHistoryResponse> getHistory(@PathVariable("history_id") Integer historyId) {
        try {
            log.info("获取面试历史记录: history_id={}", historyId);
            DetailedHistoryResponse response = historyService.getHistoryDetail(historyId);
            log.info("获取面试历史记录成功: history_id={}", historyId);
            return Result.success(response);
        } catch (HistoryNotFoundException e) {
            log.info("历史记录不存在: history_id={}", historyId);
            return Result.error(404, "历史记录不存在");
        } catch (RuntimeException e) {
            String errorMsg = "获取面试历史记录失败: " + e.getMessage();
            log.error(errorMsg, e);
            return Result.error(500, errorMsg);
        } catch (Exception e) {
            String errorMsg = "获取面试历史记录失败: " + e.getMessage();
            log.error(errorMsg, e);
            return Result.error(500, errorMsg);
        }
    }
    
    @GetMapping("/audio/{filename}")
    public ResponseEntity<Resource> getAudioFile(@PathVariable("filename") String filename) {
        try {
            log.info("收到录音文件请求: filename={}", filename);
            
            // 验证文件名格式
            if (!filename.startsWith("his-") || !filename.endsWith(".wav")) {
                log.warn("无效的文件名格式: {}", filename);
                return ResponseEntity.badRequest()
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .build();
            }
            
            // 构建文件路径
            String audioDir = "src/main/resources/uploads/audio";
            Path filePath = Paths.get(audioDir, filename);
            // 新增：打印查找的文件路径
            log.info("查找录音文件路径: {}", filePath.toAbsolutePath());
            
            // 检查文件是否存在
            if (!Files.exists(filePath)) {
                log.info("录音文件不存在: {}", filePath);
                return ResponseEntity.notFound()
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .build();
            }
            
            // 检查文件是否在uploads/audio目录下（安全验证）
            Path audioDirPath = Paths.get(audioDir).toAbsolutePath();
            if (!filePath.toAbsolutePath().startsWith(audioDirPath)) {
                log.error("尝试访问非法路径: {}", filePath);
                return ResponseEntity.status(403)
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .build();
            }
            
            // 创建文件资源
            Resource resource = new FileSystemResource(filePath.toFile());
            
            // 设置响应头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("audio/wav"));
            headers.setContentDispositionFormData("attachment", filename);
            
            log.info("返回录音文件: {}", filePath);
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(resource);
                    
        } catch (Exception e) {
            String errorMsg = "获取录音文件失败: " + e.getMessage();
            log.error(errorMsg, e);
            return ResponseEntity.status(500)
                    .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .build();
        }
    }
    
    @GetMapping("/landmark-image/{filename}")
    public ResponseEntity<Resource> getLandmarkImage(@PathVariable("filename") String filename) {
        try {
            log.info("收到landmark截图文件请求: filename={}", filename);
            
            // 放宽校验，允许三种示例图片名
            Set<String> allowedExamples = new HashSet<>(Arrays.asList(
                "example_07_landmarks.jpg",
                "example_08_landmarks.jpg",
                "example_010_landmarks.jpg"
            ));
            
            if (!((filename.startsWith("his-") && filename.endsWith("_landmarks.jpg")) || allowedExamples.contains(filename))) {
                log.warn("无效的文件名格式: {}", filename);
                return ResponseEntity.badRequest()
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .build();
            }
            
            // 构建文件路径
            String imgDir = "src/main/resources/uploads/facialLandmarks";
            Path filePath = Paths.get(imgDir, filename);
            
            // 检查文件是否存在
            if (!Files.exists(filePath)) {
                log.warn("landmark截图文件不存在: {}", filePath);
                return ResponseEntity.notFound()
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .build();
            }
            
            // 检查文件是否在facialLandmarks目录下（安全验证）
            Path imgDirPath = Paths.get(imgDir).toAbsolutePath();
            if (!filePath.toAbsolutePath().startsWith(imgDirPath)) {
                log.error("尝试访问非法路径: {}", filePath);
                return ResponseEntity.status(403)
                        .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                        .body(null);
            }
            
            // 创建文件资源
            Resource resource = new FileSystemResource(filePath.toFile());
            
            // 设置响应头
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.parseMediaType("image/jpeg"));
            headers.setContentDispositionFormData("attachment", filename);
            
            log.info("返回landmark截图文件: {}", filePath);
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(resource);
                    
        } catch (Exception e) {
            String errorMsg = "获取landmark截图文件失败: " + e.getMessage();
            log.error(errorMsg, e);
            return ResponseEntity.status(500)
                    .header(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                    .build();
        }
    }

    @GetMapping("/export")
    public void exportUserHistory(@RequestParam Long userId, HttpServletResponse response) {
        UserHistoryResponse userHistoryResponse = historyService.getUserHistory(String.valueOf(userId));
        excelService.exportUserHistoryToExcel(userHistoryResponse, response);
    }

    /**
     * 从 Excel 导入用户面试历史
     */
    @PostMapping("/import")
    public Result<Integer> importUserHistory(@RequestParam("file") MultipartFile file) {
        try {
            // 检查文件是否为空
            if (file.isEmpty()) {
                log.warn("收到空文件上传请求");
                return Result.error(400, "上传的文件为空");
            }
            
            // 检查文件类型
            String originalFilename = file.getOriginalFilename();
            if (originalFilename == null || !originalFilename.toLowerCase().endsWith(".xlsx")) {
                log.warn("不支持的文件类型: {}", originalFilename);
                return Result.error(400, "仅支持Excel文件(.xlsx)");
            }
            
            // 创建临时文件路径
            String tempDir = System.getProperty("java.io.tmpdir");
            Path tempFilePath = Files.createTempFile(Path.of(tempDir + File.separator), "upload-", ".tmp");
            
            // 保存文件到临时路径
            log.info("开始保存上传文件到临时路径: {}", tempFilePath);
            file.transferTo(tempFilePath.toFile());
            log.info("文件保存成功，大小: {} 字节", Files.size(tempFilePath));
            
            // 调用 Excel 导入服务
            log.info("开始导入Excel数据");
            int importCount = excelService.importUserHistoryFromExcel(tempFilePath.toString());
            log.info("Excel导入完成，共导入 {} 条记录", importCount);
            
            // 删除临时文件
            Files.deleteIfExists(tempFilePath);
            log.debug("临时文件已删除: {}", tempFilePath);
            
            return Result.success(importCount);
        } catch (IOException e) {
            log.error("导入Excel文件失败: {}", e.getMessage(), e);
            return Result.error(500, "文件上传失败: " + e.getClass().getName() + ": " + e.getMessage());
        } catch (Exception e) {
            log.error("未知错误导致导入失败: {}", e.getMessage(), e);
            return Result.error(500, "系统错误: " + e.getClass().getName() + ": " + e.getMessage());
        }
    }
}








