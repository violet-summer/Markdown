package com.example.layout.service.impl;

import com.example.layout.model.Sessions;
import com.example.layout.mapper.SessionsMapper;
import com.example.layout.service.ISessionsService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * <p>
 * 会话令牌表 服务实现类
 * </p>
 *
 * @author city_business
 * @since 2026-02-21
 */
@Service
public class SessionsServiceImpl extends ServiceImpl<SessionsMapper, Sessions> implements ISessionsService {

}
