package com.example.spr_swcup.service.questionBank;

import com.example.spr_swcup.dto.questionBank.TopicsResponse;
import com.example.spr_swcup.dto.questionBank.QuestionsResponse;

public interface QuestionBankService {
    /**
     * 根据RootCategory和SubCategory的name查询其下所有Topic
     * @param rootCategoryName 根分类名称
     * @param subCategoryName 二级分类名称
     * @return Topic列表及题目数量
     */
    TopicsResponse getTopics(String rootCategoryName, String subCategoryName);

    /**
     * 根据Topic的id随机查询15道Question
     * @param topicId 主题ID
     * @return 题目列表
     */
    QuestionsResponse getQuestionsByTopic(String topicId);
}
