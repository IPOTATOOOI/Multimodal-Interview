package com.example.spr_swcup.dto;

import lombok.Data;

@Data
public class QuestionDTO {
    private Integer qaId;
    private String content;
    private String keyWords;

    public QuestionDTO(Integer qaId, String content, String keyWords) {
        this.qaId = qaId;
        this.content = content;
        this.keyWords = keyWords;
    }
}
