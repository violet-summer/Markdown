package com.example.layout.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String CITY_EXCHANGE = "city-exchange";

    // 队列名称常量
    public static final String LAYOUT_RESULT_QUEUE = "layout_result";
    public static final String LAYOUT_PROGRESS_QUEUE = "layout_progress";
    public static final String MODEL_RESULT_QUEUE = "model_result";
    public static final String MODEL_PROGRESS_QUEUE = "model_progress";
    public static final String LAYOUT_TASK_QUEUE = "layout_task";
    public static final String MODEL_TASK_QUEUE = "model_task";

    @Bean
    public DirectExchange cityExchange() {
        return new DirectExchange(CITY_EXCHANGE);
    }

    // 队列声明
    @Bean
    public Queue layoutResultQueue() {
        return new Queue(LAYOUT_RESULT_QUEUE, true);
    }

    @Bean
    public Queue layoutProgressQueue() {
        return new Queue(LAYOUT_PROGRESS_QUEUE, true);
    }

    @Bean
    public Queue modelResultQueue() {
        return new Queue(MODEL_RESULT_QUEUE, true);
    }

    @Bean
    public Queue modelProgressQueue() {
        return new Queue(MODEL_PROGRESS_QUEUE, true);
    }

    @Bean
    public Queue layoutTaskQueue() {
        return new Queue(LAYOUT_TASK_QUEUE, true);
    }

    @Bean
    public Queue modelTaskQueue() {
        return new Queue(MODEL_TASK_QUEUE, true);
    }

    // 绑定：每个队列使用自己的队列名作为 routingKey
    @Bean
    public Binding layoutResultBinding() {
        return BindingBuilder.bind(layoutResultQueue())
                .to(cityExchange())
                .with(LAYOUT_RESULT_QUEUE);
    }

    @Bean
    public Binding layoutProgressBinding() {
        return BindingBuilder.bind(layoutProgressQueue())
                .to(cityExchange())
                .with(LAYOUT_PROGRESS_QUEUE);
    }

    @Bean
    public Binding modelResultBinding() {
        return BindingBuilder.bind(modelResultQueue())
                .to(cityExchange())
                .with(MODEL_RESULT_QUEUE);
    }

    @Bean
    public Binding modelProgressBinding() {
        return BindingBuilder.bind(modelProgressQueue())
                .to(cityExchange())
                .with(MODEL_PROGRESS_QUEUE);
    }

    @Bean
    public Binding layoutTaskBinding() {
        return BindingBuilder.bind(layoutTaskQueue())
                .to(cityExchange())
                .with(LAYOUT_TASK_QUEUE);
    }

    @Bean
    public Binding modelTaskBinding() {
        return BindingBuilder.bind(modelTaskQueue())
                .to(cityExchange())
                .with(MODEL_TASK_QUEUE);
    }
}