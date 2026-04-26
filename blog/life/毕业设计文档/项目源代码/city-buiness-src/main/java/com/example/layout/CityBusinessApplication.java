package com.example.layout;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.amqp.rabbit.annotation.EnableRabbit;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.kafka.annotation.EnableKafka;

@SpringBootApplication
@EnableKafka
@EnableRabbit
@MapperScan("com.example.layout.mapper")
public class CityBusinessApplication {
    public static void main(String[] args) {
        SpringApplication.run(CityBusinessApplication.class, args);
    }
}
