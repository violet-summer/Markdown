package com.example.layout.service;

import com.example.layout.model.Jobs;
import com.example.layout.model.Models;
import com.example.layout.proto.CityMqContract;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class ModelResultConsumer {

    @Autowired
    private IJobsService jobsService;
    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private IModelsService modelsService;

    @RabbitListener(queues = "model_result", concurrency = "3")
    public void onModelResponse(byte[] message) {
        System.out.println("模型生成消费 (protobuf bytes): " + message.length);
        try {
            CityMqContract.ModelTaskResultMessage resp = CityMqContract.ModelTaskResultMessage.parseFrom(message);
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getTaskId, resp.getTaskId()).eq(Jobs::getType, "model").one();
            if (job != null) {
                job.setStatus("success".equals(resp.getStatus()) ? 100 : -1);
                // Protobuf对象转JSON字符串（如需存储原始内容）
                job.setResultJson(com.google.protobuf.util.JsonFormat.printer().includingDefaultValueFields().print(resp));
                jobsService.updateById(job);
            }

            System.out.println("模型生成获取消息: " + resp.getTaskId());

            Map<String, String> paths = resp.getModelsPathsMap();
            Map<String, String> storedPaths = new HashMap<>();
            if (paths != null) {
                for (Map.Entry<String, String> entry : paths.entrySet()) {
                    String type = entry.getKey();
                    String path = entry.getValue();
                    if (path != null && !path.isBlank() && job != null) {
                        Models model = new Models();
                        model.setLayoutId(job.getLayoutId());
                        model.setUserId(job.getUserId());
                        model.setObjUrl(path);
                        model.setMtlUrl("default");
                        model.setCreatedAt(java.time.LocalDateTime.now());
                        model.setUpdatedAt(java.time.LocalDateTime.now());
                        modelsService.save(model);

                        storedPaths.put(type, path);
                    }
                }
            }
            if (job != null && !storedPaths.isEmpty()) {
                // Protobuf map转JSON字符串（如需存储）
                job.setResultJson(objectMapper.writeValueAsString(storedPaths));
                jobsService.updateById(job);
            }

        } catch (Exception e) {
            // 日志记录或异常处理
            System.out.println("模型生成消费异常: " + e.getMessage());
        }
    }
}
