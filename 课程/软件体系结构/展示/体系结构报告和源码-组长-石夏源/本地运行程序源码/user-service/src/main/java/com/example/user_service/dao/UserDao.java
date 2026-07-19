package com.example.user_service.dao;

import com.example.user_service.pojo.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserDao extends JpaRepository<User, Integer> {
    // 根据用户名查找用户
    Optional<User> findByUsername(String username);
}
