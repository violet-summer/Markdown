package org.example.service;

import org.example.dao.UserDao;
import org.example.pojo.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 用户service
 */
@Service
public class UserService {
    @Autowired
    private UserDao userDao;
    /**     * 查询所有用户     */
    public List<User> findAll(){        return userDao.findAll();    }
    /**     * 根据id查询用户     */
    public User findById(Integer id){        return userDao.findById(id).get();    }
    /**     * 添加用户     */
    public void add(User user){        userDao.save(user);    }
    /**     * 修改用户  up    */
    public void update(User user){         userDao.save(user);    }
    /**     * 根据id删除用户     */
    public void deleteById(Integer id){        userDao.deleteById(id);    }
}