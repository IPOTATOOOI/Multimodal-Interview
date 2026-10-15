package com.example.spr_swcup.model;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class User {
    private Long userId;
    private String username;
    private String password;
    private LocalDateTime createdAt;


}