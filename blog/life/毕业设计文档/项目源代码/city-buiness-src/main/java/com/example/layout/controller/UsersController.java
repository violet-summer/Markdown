package com.example.layout.controller;

import com.example.citybusiness.contract.api.UsersApi;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequestMapping("/api/users")
public class UsersController implements UsersApi {

//    查询用户的配置信息
    @GetMapping("/config")
    public String getUserConfig() {
        return "用户配置信息";
    }

    // 获取当前用户信息
//    @GetMapping("/me")
//    public UserMeResponse getMe() {
//        UserMeResponse user = new UserMeResponse();
//        user.setUsername("test_user"); // 实际应从认证信息获取
//        user.setEmail("test@example.com");
//        return user;
//    }
//
//    // 更新当前用户信息
//    @PatchMapping("/me")
//    public UserMeResponse updateMe(@RequestBody UserMeResponse payload) {
//        // 实际应更新数据库，这里仅模拟返回
//        UserMeResponse user = new UserMeResponse();
//        user.setUsername(payload.getUsername() != null ? payload.getUsername() : "test_user");
//        user.setEmail(payload.getEmail() != null ? payload.getEmail() : "test@example.com");
//        return user;
//    }

}
