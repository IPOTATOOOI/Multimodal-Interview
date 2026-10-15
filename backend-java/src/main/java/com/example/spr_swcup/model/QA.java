package com.example.spr_swcup.model;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.Data;
@Data
@Entity
public class QA {
    @Id
    private Integer qaId;
    private String content;
    private String keyWords;
    private Integer historyId;
}
