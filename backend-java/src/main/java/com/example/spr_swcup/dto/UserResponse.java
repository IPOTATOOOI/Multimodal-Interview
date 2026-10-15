
// UserResponse.java
package com.example.spr_swcup.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class UserResponse {
    private String username;
    private LocalDateTime createdAt;
}