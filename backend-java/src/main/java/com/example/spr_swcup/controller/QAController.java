package com.example.spr_swcup.controller;

import com.example.spr_swcup.dto.QuestionDTO;
import com.example.spr_swcup.model.QA;
import com.example.spr_swcup.repository.QARepository;
import com.example.spr_swcup.service.CustomException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
public class QAController {

    private final QARepository qaRepository;

    public QAController(QARepository qaRepository) {
        this.qaRepository = qaRepository;
    }

    @GetMapping("/getQuestion")
    @CrossOrigin(origins = "${CORS_ORIGINS:http://localhost:5173}")
    public ResponseEntity<?> getQuestion(
            @RequestParam(name = "history") Integer history
    ) {
        try {
            List<QA> results = qaRepository.findByHistoryId(history);

            if (results.isEmpty()) {
                return ResponseEntity.ok().body(new ResponseDto(List.of()));
            }

            List<QuestionDTO> dtos = results.stream()
                    .map(qa -> new QuestionDTO(
                            qa.getQaId(),
                            qa.getContent(),
                            qa.getKeyWords()
                    ))
                    .collect(Collectors.toList());

            return ResponseEntity.ok().body(new ResponseDto(dtos));

        } catch (Exception e) {
            throw new CustomException("数据库查询失败: " + e.getMessage());
        }
    }

    // 响应包装类
    private static class ResponseDto {
        private List<QuestionDTO> questions;

        public ResponseDto(List<QuestionDTO> questions) {
            this.questions = questions;
        }

        public List<QuestionDTO> getQuestions() {
            return questions;
        }
    }
}
