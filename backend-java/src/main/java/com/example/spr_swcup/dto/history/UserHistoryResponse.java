package com.example.spr_swcup.dto.history;

import lombok.Data;

import java.util.List;
import java.io.Serializable;

@Data
public class UserHistoryResponse {
    //private static final long serialVersionUID = 1L;
    private String userId;
    private Integer total;
    private List<BasicHistoryDTO> historyList;
} 