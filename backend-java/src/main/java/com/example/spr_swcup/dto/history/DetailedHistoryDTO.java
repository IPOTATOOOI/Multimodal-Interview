package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.util.Date;

@Data
public class DetailedHistoryDTO {
    private Integer historyId;
    private String userId;
    private Date interviewTime;
    private Date endTime;
    private String field;
    private String position;
    private Integer professionalKnowledge;
    private Integer skillMatch;
    private Integer languageExpression;
    private Integer logicalThinking;
    private Integer innovationAbility;
    private Integer stressResistance;
    private String feedbackSuggestion1;
    private String feedbackSuggestion2;
    private String feedbackSuggestion3;
    private String html;
    private Date createdAt;
    private Integer score;
} 