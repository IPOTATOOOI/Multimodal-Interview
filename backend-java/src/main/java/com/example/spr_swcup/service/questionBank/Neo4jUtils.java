package com.example.spr_swcup.service.questionBank;

/**
 * Neo4j工具类，用于处理类型转换
 */
public class Neo4jUtils {
    
    /**
     * 安全地将Neo4j返回的数值转换为Integer
     * @param value 从Neo4j获取的值
     * @return Integer值，如果转换失败返回null
     */
    public static Integer safeToInteger(Object value) {
        if (value == null) {
            return null;
        }
        
        if (value instanceof Integer) {
            return (Integer) value;
        }
        
        if (value instanceof Long) {
            return ((Long) value).intValue();
        }
        
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        
        try {
            return Integer.valueOf(value.toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }
    
    /**
     * 安全地将Neo4j返回的数值转换为Long
     * @param value 从Neo4j获取的值
     * @return Long值，如果转换失败返回null
     */
    public static Long safeToLong(Object value) {
        if (value == null) {
            return null;
        }
        
        if (value instanceof Long) {
            return (Long) value;
        }
        
        if (value instanceof Integer) {
            return ((Integer) value).longValue();
        }
        
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        
        try {
            return Long.valueOf(value.toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }
} 