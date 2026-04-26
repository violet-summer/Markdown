package com.example.layout.service;

import com.example.citybusiness.contract.model.RegisterResponse;
import com.example.layout.model.Users;
import com.baomidou.mybatisplus.extension.service.IService;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author city_business
 * @since 2026-02-18
 */
public interface IUsersService extends IService<Users> {
    RegisterResponse register(String username, String email, String password);
    RegisterResponse login(String identifier, String password);
}
