package com.example.user_service.service;

import com.example.user_service.DTO.LoginDTO;
import com.example.user_service.DTO.RegisterDTO;
import com.example.user_service.dao.UserDao;
import com.example.user_service.pojo.User;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;

@Service
public class UserService {

    private final UserDao userDao;

    public UserService(UserDao userDao) {
        this.userDao = userDao;
    }

    public Boolean Login(LoginDTO loginDTO){
        User user = userDao.findByUsername(loginDTO.getUsername()).orElse(null);
        if(user == null){
            return false;
        } else {
            return user.getPassword().equals(loginDTO.getPassword());
        }
    }
    public Boolean Register(RegisterDTO registerDTO){
        User user = userDao.findByUsername(registerDTO.getUsername()).orElse(null);
        if(user != null){
            return false;
        } else {
            user = new User();
            user.setUsername(registerDTO.getUsername());
            user.setPassword(registerDTO.getPassword());
            user.setEmail(registerDTO.getEmail());
            user.setCreatedAt(LocalDateTime.ofInstant(Instant.ofEpochMilli(System.currentTimeMillis()), ZoneId.systemDefault()));
            userDao.save(user);
            return true;
        }
    }
}
