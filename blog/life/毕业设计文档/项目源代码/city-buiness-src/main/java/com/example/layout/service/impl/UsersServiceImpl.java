package com.example.layout.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import com.example.citybusiness.contract.model.RegisterResponse;
import com.example.layout.mapper.UsersMapper;
import com.example.layout.model.Users;
import com.example.layout.service.IUsersService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author city_business
 * @since 2026-02-18
 */
@Service
public class UsersServiceImpl extends ServiceImpl<UsersMapper, Users> implements IUsersService {

    @Autowired
    private UsersMapper usersMapper;

    public RegisterResponse register(String username, String email, String password) {
        // 检查邮箱或用户名是否已存在
        if (usersMapper.selectOne(new QueryWrapper<Users>().eq("email", email)) != null ||
            usersMapper.selectOne(new QueryWrapper<Users>().eq("username", username)) != null) {
            throw new RuntimeException("User already exists");
        }
        // 密码加密
        String hashed = com.example.layout.utils.security.hashPassword(password);
        Users user = new Users();
        user.setUsername(username);
        user.setEmail(email);
        user.setPasswordHash(hashed);
        usersMapper.insert(user);

        // 生成 token
        String token = com.example.layout.utils.security.createAccessToken(user.getId().toString());
        RegisterResponse response = new RegisterResponse();
response.setUserId(user.getId().toString());
response.setToken(token);
response.setUsername(user.getUsername());
response.setEmail(user.getEmail());
return response;

         }

    public RegisterResponse login(String identifier, String password) {
        // 先尝试用邮箱查找
        Users user = usersMapper.selectOne(new QueryWrapper<Users>().eq("email", identifier));
        // 如果邮箱查不到，再用用户名查找
        if (user == null) {
            user = usersMapper.selectOne(new QueryWrapper<Users>().eq("username", identifier));
        }
        // 用户不存在或密码不正确
        if (user == null || !com.example.layout.utils.security.verifyPassword(password, user.getPasswordHash())) {
            throw new RuntimeException("Invalid credentials");
        }
        // 生成 token
        String token = com.example.layout.utils.security.createAccessToken(user.getId().toString());
                RegisterResponse response = new RegisterResponse();
response.setUserId(user.getId().toString());
response.setToken(token);
response.setUsername(user.getUsername());
response.setEmail(user.getEmail());
return response;
//        return new RegisterResponse(token, user.getId().toString(), user.getUsername(), user.getEmail());
    }
}
