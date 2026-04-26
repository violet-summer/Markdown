package com.example.layout.service;
import com.google.protobuf.util.JsonFormat;


import com.example.layout.model.Jobs;
import com.example.layout.model.Layouts;
import com.example.layout.proto.CityMqContract;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.time.LocalDateTime;
import org.springframework.beans.factory.annotation.Autowired;

@Service
public class LayoutResultConsumer {

    @Autowired
    private IJobsService jobsService;
    @Autowired
    private ObjectMapper objectMapper;
    @Autowired
    private ILayoutsService layoutsService;

    /**
     * RabbitMQ消息结构体消费：布局生成响应
     */
    @RabbitListener(queues = "layout_result", concurrency = "3")
    public void onLayoutResponse(byte[] message) {
        try {
            CityMqContract.LayoutTaskResultMessage resp = CityMqContract.LayoutTaskResultMessage.parseFrom(message);
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getTaskId, resp.getTaskId()).eq(Jobs::getType, "layout").one();
            if (job != null) {
                job.setStatus("success".equals(resp.getStatus()) ? 100: -1);
                System.out.println("响应内容"+resp);
                // 序列化为JSON字符串
                // 使用 Protobuf JsonFormat 序列化
                String json = com.google.protobuf.util.JsonFormat.printer().includingDefaultValueFields().print(resp);
                job.setResultJson(json);
                jobsService.updateById(job);
                // 仅在成功时写入 Layouts
                System.out.println("查询到作业"+job);
                if ("success".equals(resp.getStatus())) {
                    // 避免重复写入
                    System.out.println("布局生成获取消息: " + resp.getTaskId());
                    Layouts exist = layoutsService.lambdaQuery().eq(Layouts::getId, job.getLayoutId()).one();
                    if (exist == null) {
                        Layouts layout = new Layouts();
                        layout.setId(job.getLayoutId());
                        layout.setUserId(job.getUserId());
                        layout.setCreatedAt(LocalDateTime.now());
                        layout.setStatus(2);
                        layout.setParamsJson(job.getPayloadJson());
                        String layout_dir_path = "assets/" + job.getUserId() + "/" + job.getLayoutId() + "/";
                        layout.setSvgUrl(resp.getSvgUrl()); // 假设 resp 里有 svgUrl 字段
                        layoutsService.save(layout);
                    }
                }
            }
        } catch (Exception e) {
            // 日志记录或异常处理
            System.err.println("处理布局生成结果时发生错误: " + e.getMessage());
        }
    }
}
