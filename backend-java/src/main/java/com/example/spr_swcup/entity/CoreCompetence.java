package com.example.spr_swcup.entity;

import lombok.Data;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
public class CoreCompetence {
    private Long competenceId;
    private Long positionId;
    private String competenceName;
    private String competenceDescription;
}
