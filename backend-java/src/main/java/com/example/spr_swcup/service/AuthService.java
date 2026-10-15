package com.example.spr_swcup.service;
import com.example.spr_swcup.dto.UserLoginRequest;
import com.example.spr_swcup.dto.UserRegistrationRequest;
import com.example.spr_swcup.model.User;
import com.example.spr_swcup.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import java.util.Optional;
@Service
public class AuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public void register(UserRegistrationRequest request) {
        Optional<User> existingUser = userRepository.findByUsername(request.getUsername());
        if (existingUser.isPresent()) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "用户名已经注册");
        }

        String hashedPassword = passwordEncoder.encode(request.getPassword());
        int result = userRepository.save(request.getUsername(), hashedPassword);

        if (result != 1) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "数据库错误");
        }
    }

    public User authenticate(UserLoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "用户名或密码错误");
        }

        return user;
    }
}
