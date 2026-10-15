package com.example.spr_swcup.dto.questionBank;

import lombok.Data;
import java.util.List;

@Data
public class QuestionsResponse {
    private List<QuestionDTO> questions;
} 