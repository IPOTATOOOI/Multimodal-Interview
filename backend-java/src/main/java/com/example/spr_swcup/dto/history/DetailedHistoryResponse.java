package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.util.List;

@Data
public class DetailedHistoryResponse {
    private DetailedHistoryDTO interviewHistory;
    private List<QADTO> qaLog;
    private List<String> landmarkImages;
} 