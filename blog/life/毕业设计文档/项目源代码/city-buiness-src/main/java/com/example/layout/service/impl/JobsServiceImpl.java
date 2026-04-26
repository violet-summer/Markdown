package com.example.layout.service.impl;

import com.example.layout.model.Jobs;
import com.example.layout.mapper.JobsMapper;
import com.example.layout.service.IJobsService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * <p>
 * 任务表 服务实现类
 * </p>
 *
 * @author city_business
 * @since 2026-02-21
 */
@Service
public class JobsServiceImpl extends ServiceImpl<JobsMapper, Jobs> implements IJobsService {

}
