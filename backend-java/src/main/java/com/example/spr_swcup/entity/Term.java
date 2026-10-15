package com.example.spr_swcup.entity;

import lombok.Data;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
public class Term {
    private Long termId;
    private Long positionId;
    private String termName;
    private String termExplanation;
    private String frequency;
}

