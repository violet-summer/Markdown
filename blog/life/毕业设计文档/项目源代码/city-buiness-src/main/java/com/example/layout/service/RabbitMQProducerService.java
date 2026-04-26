package com.example.layout.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.protobuf.MessageLite;

@Service
public class RabbitMQProducerService {
    private static final String DEFAULT_EXCHANGE = "city-exchange";
    private static final String DEFAULT_ROUTING_KEY = "city-routing-key";

    @Autowired
    private RabbitTemplate rabbitTemplate;
    @Autowired
    private ObjectMapper objectMapper;

    /**
     * 发送protobuf消息
     */
    public void sendProtoMessage(String exchange, String routingKey, MessageLite protoMessage) {
        byte[] data = protoMessage.toByteArray();
        rabbitTemplate.convertAndSend(exchange, routingKey, data);
    }

    /**
     * 兼容原有Object消息（如JSON），建议逐步废弃
     */
    public void sendMessage(String exchange, String routingKey, Object message) {
        try {
            String json = objectMapper.writeValueAsString(message);
            rabbitTemplate.convertAndSend(exchange, routingKey, json);
        } catch (Exception e) {
            throw new RuntimeException("RabbitMQ消息序列化失败", e);
        }
    }

    /**
     * 兼容原有字符串消息（如调试），建议逐步废弃
     */
    public void sendMessage(String message) {
        rabbitTemplate.convertAndSend(DEFAULT_EXCHANGE, DEFAULT_ROUTING_KEY, message);
    }
}
