package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.math.BigDecimal;
import java.util.Date;

@Data
public class QADTO {
    private Integer qaId;
    private Integer historyId;
    // 0 = 问题，1 = 回答
    private Integer role;
    private String content;
    private Date createdAt;
    private String evaluation;
    private String feedback;
    private String keyWords;
    private String referenceA;
    private String difficulty;
    private String skill;
    private BigDecimal answerRating;
    private String category;
    // 录音文件路径
    private String audioFile;
}