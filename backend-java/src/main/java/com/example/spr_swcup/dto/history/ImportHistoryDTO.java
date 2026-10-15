package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.util.Date;

@Data
public class ImportHistoryDTO {
    private Integer historyId;
    // 改为Integer类型以匹配数据库实际结构
    private Integer userId;
    private Date interviewTime;
    private String field;
    private String position;
    private Integer professionalKnowledge;
    private Integer skillMatch;
    private Integer languageExpression;
    private Integer logicalThinking;
    private Integer innovationAbility;
    private Integer stressResistance;
    private String feedbackSuggestion1;
    private Integer score;
    private Date endTime;
    private Date createdAt;
}