package com.example.config;

import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.server.reactive.HttpHandler;
import org.springframework.web.reactive.DispatcherHandler;
import org.springframework.web.server.adapter.WebHttpHandlerBuilder;

@Configuration
public class CustomHttpHandlerConfig {

    @Bean
    public HttpHandler httpHandler(ApplicationContext context) {
        DispatcherHandler dispatcherHandler = new DispatcherHandler(context);
        return WebHttpHandlerBuilder.webHandler(dispatcherHandler).build();
    }
}
