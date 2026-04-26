package com.example.layout.service;

import com.example.layout.model.Jobs;
import com.example.layout.proto.CityMqContract;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class ModelProgressConsumer {

    @Autowired
    private IJobsService jobsService;
    @Autowired
    private ObjectMapper objectMapper;

    @RabbitListener(queues = "model_progress", concurrency = "3")
    public void listenModelProgress(byte[] message) {
        try {
            CityMqContract.LayoutProgressMessage progress = CityMqContract.LayoutProgressMessage.parseFrom(message);
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getTaskId, progress.getTaskId()).eq(Jobs::getType, "model").one();
            if (job != null) {
                int statusInt = mapStatus(progress.getStatus(), progress.getProgress());
                job.setStatus(statusInt);
                jobsService.updateById(job);
            }
        } catch (Exception e) {
            // 日志记录或异常处理
            System.out.println("模型进度问题"+e.getMessage());
        }
    }

    private int mapStatus(String status, Integer progress) {
        if (status == null) return 0;
        switch (status) {
            case "start_generate_models":
                return 10;
            case "generating_models":
                return 80;
            case "completed":
                return 100;
            case "phase2":
                return 4;
            case "done":
                return 10;
            case "failed":
                return -1;
            default:
                if (progress != null && progress >= 100) return 10;
                return 2;
        }
    }
}
