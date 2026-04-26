package com.example.layout.controller;

import com.example.citybusiness.contract.model.LoginRequest;

import com.example.citybusiness.contract.model.RegisterRequest;
import com.example.citybusiness.contract.model.RegisterResponse;
import com.example.layout.dto.ApiResponse;
import com.example.layout.service.IUsersService;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);

    private final IUsersService usersService;

    @Autowired
    public AuthController(IUsersService usersService) {
        this.usersService = usersService;
    }

    @PostMapping("/login")
    public ApiResponse<RegisterResponse> login(@RequestBody LoginRequest payload) {
        try {
            logger.info("[AUTH] Login attempt - identifier={}", payload.getIdentifier());

            RegisterResponse data = usersService.login(payload.getIdentifier(), payload.getPassword());
            logger.info("[AUTH] Login success - user_id={}", data.getUserId());
            // 登录成功后返回token
            return new ApiResponse<>(200, "OK", data);
        } catch (Exception exc) {
            logger.warn("[AUTH] Login failed - identifier={}, error={}", payload.getIdentifier(), exc.getMessage());
            return new ApiResponse<>(401, exc.getMessage(), null);
        }
    }

    @PostMapping("/register")
    public ApiResponse<RegisterResponse> register(@RequestBody RegisterRequest payload) {
        try {
            logger.info("[AUTH] Register attempt - username={}, email={}", payload.getUserName(), payload.getEmail());
            RegisterResponse data = usersService.register(payload.getUserName(), payload.getEmail(), payload.getPassword());
            logger.info("[AUTH] Register success - username={}", payload.getUserName());
            return new ApiResponse<>(200, "OK", data);
        } catch (Exception exc) {
            logger.warn("[AUTH] Register failed - username={}, error={}", payload.getUserName(), exc.getMessage());
            return new ApiResponse<>(400, exc.getMessage(), null);
        }
    }
}
