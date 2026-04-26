package com.example.layout.service;

import com.example.layout.model.Jobs;
import com.example.layout.proto.CityMqContract;
import com.example.layout.service.IJobsService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class LayoutProgressConsumer {

    @Autowired
    private IJobsService jobsService;
    @Autowired
    private ObjectMapper objectMapper;

    @RabbitListener(queues = "layout_progress", concurrency = "3")
      public void listenLayoutProgress(byte[] message) {
          System.out.println("[RabbitMQ] layout_progress 消费收到消息 (protobuf bytes): " + message.length);
          try {
              CityMqContract.LayoutProgressMessage progress = CityMqContract.LayoutProgressMessage.parseFrom(message);
              System.out.println("[RabbitMQ] layout_progress 反序列化后: taskId=" + progress.getTaskId() + ", status=" + progress.getStatus() + ", progress=" + progress.getProgress());
              Jobs job = jobsService.lambdaQuery().eq(Jobs::getTaskId, progress.getTaskId()).eq(Jobs::getType, "layout").one();
              if (job != null) {
                  int statusInt = mapStatus(progress.getStatus(), progress.getProgress());
                  job.setStatus(statusInt);
                  jobsService.updateById(job);
                  System.out.println("[RabbitMQ] layout_progress 更新 job 状态: " +progress.getStatus()+":"+ statusInt);
              } else {
                  System.out.println("[RabbitMQ] layout_progress 未找到对应 job: taskId=" + progress.getTaskId());
              }
          } catch (Exception e) {
              System.err.println("[RabbitMQ] layout_progress 消费异常: " + e.getMessage());
          }
    }

    private int mapStatus(String status, Integer progress) {
        if (status == null) return 0;
        return switch (status) {
            case "stage_0" -> 10; // 基础布局生成
            case "stage_1" -> 20; // 水线生成
            case "stage_2" -> 30; // 水域多边形生成
            case "stage_3" -> 40; // 主干道生成
            case "stage_4" -> 50; // 大型公园生成
            case "stage_5" -> 60; // 次级道路生成
            case "stage_6" -> 70; // 小型公园生成
            case "stage_7" -> 80; // 多边形布局生成
            case "stage_8" -> 90; // 导出SVG与JSON
            case "completed" -> 100; // 完成
            case "failed" -> -1; // 失败
            case "start_generate_models" -> 1; // 已接收
            default -> {
                if (progress != null && progress >= 100) yield 100;
                yield 1;
            }
        };
    }
}
