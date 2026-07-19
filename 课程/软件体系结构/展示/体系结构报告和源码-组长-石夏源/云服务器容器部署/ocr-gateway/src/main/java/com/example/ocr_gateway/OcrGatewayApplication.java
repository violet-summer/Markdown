package com.example.ocr_gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.web.reactive.WebFluxAutoConfiguration;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.context.annotation.ComponentScan;


@EnableDiscoveryClient
@ComponentScan("com.example")
@SpringBootApplication
public class OcrGatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(OcrGatewayApplication.class, args);
    }

}
