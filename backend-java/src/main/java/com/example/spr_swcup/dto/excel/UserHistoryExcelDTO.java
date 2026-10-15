package com.example.spr_swcup.dto.excel;

import com.alibaba.excel.annotation.ExcelProperty;
import com.alibaba.excel.annotation.format.DateTimeFormat;
import lombok.Data;

import java.util.Date;

@Data
public class UserHistoryExcelDTO {

    @ExcelProperty("历史记录ID")
    private Long historyId;

    @ExcelProperty("面试时间")
    @DateTimeFormat("yyyy-MM-dd HH:mm:ss")
    private Date interviewTime;

    @ExcelProperty("领域")
    private String field;

    @ExcelProperty("岗位")
    private String position;

    @ExcelProperty("专业知识评分")
    private Integer professionalKnowledge;

    @ExcelProperty("技能匹配评分")
    private Integer skillMatch;

    @ExcelProperty("语言表达评分")
    private Integer languageExpression;

    @ExcelProperty("逻辑思维评分")
    private Integer logicalThinking;

    @ExcelProperty("创新能力评分")
    private Integer innovationAbility;

    @ExcelProperty("抗压能力评分")
    private Integer stressResistance;

    @ExcelProperty("反馈建议")
    private String feedbackSuggestion1;

    @ExcelProperty("总分")
    private Integer score;

    @ExcelProperty("结束时间")
    @DateTimeFormat("yyyy-MM-dd HH:mm:ss")
    private Date endTime;
}