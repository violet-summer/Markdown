package org.example.client;

import org.example.pojo.User;
import org.springframework.stereotype.Component;

@Component
public class UserControllerImpl implements UserController{
    @Override
    public User findById(Integer id){
        System.out.println("执行了熔断器类……");
        return null;
    }
}
