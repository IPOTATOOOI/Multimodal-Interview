package com.example.spr_swcup.service.history;

/**
 * 历史记录不存在异常
 */
public class HistoryNotFoundException extends RuntimeException {
    
    public HistoryNotFoundException(String message) {
        super(message);
    }
    
    public HistoryNotFoundException(String message, Throwable cause) {
        super(message, cause);
    }
} 