package com.example.spr_swcup.repository;

import com.example.spr_swcup.model.User;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

@Repository
@Slf4j
public class UserRepository {

    private final JdbcTemplate jdbcTemplate;

    @Autowired
    public UserRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public Optional<User> findByUsername(String username) {
        String sql = "SELECT user_id, username, password, created_at FROM user WHERE username = ?";
        try {
//            User user = jdbcTemplate.queryForObject(sql, new Object[]{username}, new UserRowMapper());
            List<User> userList = jdbcTemplate.query(sql, new UserRowMapper(),  username);
            log.info("userList: {}", userList);
            User user = userList.get(0);
            return Optional.ofNullable(user);
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    public int save(String username, String password) {
        String sql = "INSERT INTO user (username, password) VALUES (?, ?)";
        return jdbcTemplate.update(sql, username, password);
    }

    private static class UserRowMapper implements RowMapper<User> {
        @Override
        public User mapRow(ResultSet rs, int rowNum) throws SQLException {
            User user = new User();
            user.setUserId((long) rs.getInt("user_id"));
            user.setUsername(rs.getString("username"));
            user.setPassword(rs.getString("password"));
            user.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
            return user;
        }
    }
}