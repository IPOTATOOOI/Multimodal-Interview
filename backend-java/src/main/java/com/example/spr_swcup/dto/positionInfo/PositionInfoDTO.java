package com.example.spr_swcup.dto.positionInfo;

import com.example.spr_swcup.entity.CoreCompetence;
import com.example.spr_swcup.entity.HighFreqQuestion;
import com.example.spr_swcup.entity.Term;
import lombok.Data;

import java.util.List;

/**
 * @author lty
 * @version 1.0
 * {@code @description:}
 * @since 2025-07-19
 */
@Data
public class PositionInfoDTO {
    private List<CoreCompetence> coreCompetences;
    private List<Term> terms;
    private List<HighFreqQuestion> highFreqQuestions;
}
