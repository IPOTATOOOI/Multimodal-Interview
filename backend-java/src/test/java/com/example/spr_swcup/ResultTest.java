package com.example.spr_swcup;

import com.example.spr_swcup.common.Result;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class ResultTest {
    @Test
    public void testSuccessWithIntegerData() {
        Integer testData = 123;
        Result<Integer> result = Result.success(testData);

        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals("操作成功", result.getMessage());
        assertEquals(testData, result.getData());
    }
    
    @Test
    public void testSuccessWithStringData() {
        String testData = "test data";
        // 使用Object类型变量接收String数据，避免方法重载歧义
        Object data = testData;
        Result<Object> result = Result.success(data);
        
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals("操作成功", result.getMessage());
        assertEquals(testData, result.getData());
    }
    
    @Test
    public void testSuccessWithMessage() {
        // 创建一个只有消息的成功响应
        String message = "操作完成";
        Result<String> result = Result.success(message);
        
        // 验证结果
        assertNotNull(result);
        assertEquals(200, result.getCode());
        assertEquals(message, result.getMessage());
        assertEquals(null, result.getData());
    }
    
    @Test
    public void testFail() {
        // 创建一个失败响应
        Result<String> result = Result.fail(400, "参数错误");
        
        // 验证结果
        assertNotNull(result);
        assertEquals(400, result.getCode());
        assertEquals("参数错误", result.getMessage());
        assertEquals(null, result.getData());
    }
    
    @Test
    public void testError() {
        // 创建一个错误响应
        Result<String> result = Result.error(500, "服务器内部错误");
        
        // 验证结果
        assertNotNull(result);
        assertEquals(500, result.getCode());
        assertEquals("服务器内部错误", result.getMessage());
        assertEquals(null, result.getData());
    }
    
    @Test
    public void testConstructors() {
        // 测试无参构造函数
        Result<String> result1 = new Result<>();
        assertNull(result1.getCode());
        assertNull(result1.getMessage());
        assertNull(result1.getData());
        
        // 测试两个参数的构造函数
        Result<String> result2 = new Result<>(200, "成功");
        assertEquals(200, result2.getCode());
        assertEquals("成功", result2.getMessage());
        assertNull(result2.getData());
        
        // 测试三个参数的构造函数
        Result<String> result3 = new Result<>(200, "成功", "数据");
        assertEquals(200, result3.getCode());
        assertEquals("成功", result3.getMessage());
        assertEquals("数据", result3.getData());
    }
    
    @Test
    public void testDeprecatedMethod() {
        Result<String> result = Result.oldErrorMethod(500, "旧的错误方法");
        
        assertNotNull(result);
        assertEquals(500, result.getCode());
        assertEquals("旧的错误方法", result.getMessage());
        assertEquals(null, result.getData());
    }
}