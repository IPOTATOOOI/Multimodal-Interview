package com.example.spr_swcup.dto.questionBank;

import lombok.Data;
import java.util.List;

@Data
public class QuestionDTO {
    private String id;
    private String title;
    private String content;
    private String choice;
    private String type;
    private String difficulty;
    private String answer;
    private List<TagDTO> tags;
    private List<KnowledgePointDTO> knowledgePoints;
}
