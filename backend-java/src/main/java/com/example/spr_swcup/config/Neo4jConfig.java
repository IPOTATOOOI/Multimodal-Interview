package com.example.spr_swcup.config;

import lombok.extern.slf4j.Slf4j;
import org.neo4j.driver.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Slf4j
@Configuration
public class Neo4jConfig {
    
    @Value("${spring.neo4j.uri}")
    private String uri;
    
    @Value("${spring.neo4j.authentication.username}")
    private String username;
    
    @Value("${spring.neo4j.authentication.password}")
    private String password;
    
    @Bean
    public Driver neo4jDriver() {
        try {
            Driver driver = GraphDatabase.driver(uri, AuthTokens.basic(username, password));
            // 测试连接
            try (Session session = driver.session()) {
                session.run("RETURN 1 as test");
                log.info("Neo4j数据库连接成功");
            }
            return driver;
        } catch (Exception e) {
            log.error("Neo4j数据库连接失败: {}", e.getMessage());
            throw new RuntimeException("Neo4j数据库连接失败", e);
        }
    }
} 