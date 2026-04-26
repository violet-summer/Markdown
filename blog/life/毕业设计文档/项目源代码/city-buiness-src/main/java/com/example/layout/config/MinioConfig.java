package com.example.layout.config;

import io.minio.MinioClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MinioConfig {
    // 可通过 application.yml 配置这些参数
    @Value("${minio.connect-timeout:5000}")
    private int connectTimeoutMs;
    @Value("${minio.read-timeout:30000}")
    private int readTimeoutMs;
    @Value("${minio.write-timeout:30000}")
    private int writeTimeoutMs;
    @Value("${minio.max-idle-connections:20}")
    private int maxIdleConnections;
    @Value("${minio.keep-alive-duration:5}")
    private int keepAliveDurationMinutes;

    @Bean
    public okhttp3.OkHttpClient minioOkHttpClient() {
        return new okhttp3.OkHttpClient.Builder()
                .connectTimeout(connectTimeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS)
                .readTimeout(readTimeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS)
                .writeTimeout(writeTimeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS)
                .connectionPool(new okhttp3.ConnectionPool(
                        maxIdleConnections,
                        keepAliveDurationMinutes, java.util.concurrent.TimeUnit.MINUTES))
                .retryOnConnectionFailure(true)
                .build();
    }

    @Value("${minio.endpoint}")
    private String endpoint;

    @Value("${minio.access-key}")
    private String accessKey;

    @Value("${minio.secret-key}")
    private String secretKey;

    @Bean
    public MinioClient minioClient() {
        return MinioClient.builder()
                .endpoint(endpoint)
                .credentials(accessKey, secretKey)
                .httpClient(minioOkHttpClient())
                .build();
    }
}
