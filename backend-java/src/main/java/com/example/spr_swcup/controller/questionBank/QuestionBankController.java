package com.example.spr_swcup.controller.questionBank;

import com.example.spr_swcup.common.Result;
import com.example.spr_swcup.dto.questionBank.TopicsResponse;
import com.example.spr_swcup.dto.questionBank.QuestionsResponse;
import com.example.spr_swcup.service.questionBank.QuestionBankService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
@RequestMapping("/question-bank")
public class QuestionBankController {

    @Autowired
    private QuestionBankService questionBankService;

    @GetMapping("/topics")
    public Result<TopicsResponse> getTopics(
            @RequestParam("root_category_name") String rootCategoryName,
            @RequestParam("sub_category_name") String subCategoryName) {
        try {
            log.info("获取Topic列表: rootCategoryName={}, subCategoryName={}", rootCategoryName, subCategoryName);

            TopicsResponse response = questionBankService.getTopics(rootCategoryName, subCategoryName);

            log.info("获取Topic列表成功: count={}", response.getTopics().size());
            return Result.success(response);

        } catch (RuntimeException e) {
            if ("RootCategory或SubCategory不存在".equals(e.getMessage())) {
                log.info("分类不存在: rootCategoryName={}, subCategoryName={}", rootCategoryName, subCategoryName);
                return Result.error(404, e.getMessage());
            }
            String errorMsg = "获取Topic列表失败: " + e.getMessage();
            log.error(errorMsg, e);
            return Result.error(500, errorMsg);
        } catch (Exception e) {
            String errorMsg = "获取Topic列表失败: " + e.getMessage();
            log.error(errorMsg, e);
            return Result.error(500, errorMsg);
        }
    }

    @GetMapping("/questions")
    public Result<QuestionsResponse> getQuestionsByTopic(
            @RequestParam("topic_id") String topicId) {
        try {
            log.info("获取Question列表: topicId={}", topicId);

            QuestionsResponse response = questionBankService.getQuestionsByTopic(topicId);

            log.info("获取Question列表成功: count={}", response.getQuestions().size());
            return Result.success(response);

        } catch (Exception e) {
            log.error("获取Question列表失败", e);
            return Result.error(500, "获取Question列表失败: " + e.getMessage());
        }
    }
}
