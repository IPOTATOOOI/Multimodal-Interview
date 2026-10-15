package com.example.spr_swcup.entity;

import lombok.Data;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
public class HighFreqQuestion {
    private Long questionTypeId;
    private Long positionId;
    private String questionTypeName;
    private String questionExample;
    private String scoringFocus;
    private String answerTemplate;
}
