package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.util.Date;

@Data
public class BasicHistoryDTO {
    //private static final long serialVersionUID = 1L;
    private Integer historyId;
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
}
/*
history_id： int （主键，自动生成）
user_id： varchar (50) （外键，关联用户表）
interview_time： datetime （面试时间）
field： varchar (50) （选择的技术领域）
position： varchar (50) （选择的岗位）
professional_knowledge： int （专业知识水平，1-5 分）
skill_match： int （技能匹配度，1-5 分）
language_expression： int （语言表达能力，1-5 分）
logical_thinking： int （逻辑思维能力，1-5 分）
innovation_ability： int （创新能力，1-5 分）
stress_resistance： int （应变抗压能力，1-5 分）
feedback_suggestion1： text （反馈建议 1）
feedback_suggestion2： text （反馈建议 2）
feedback_suggestion3： text （反馈建议 3）
html： text （大模型生成的 HTML）
created_at： datetime （面试时间，ID生成时记录）
score：int （面试分数）
end_time：datetime （面试结束时间）
 */
