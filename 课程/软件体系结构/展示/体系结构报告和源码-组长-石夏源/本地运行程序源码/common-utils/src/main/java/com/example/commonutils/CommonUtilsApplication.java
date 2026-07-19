package com.example.commonutils;

import com.alibaba.nacos.api.NacosFactory;
import com.alibaba.nacos.api.config.ConfigService;
import com.alibaba.nacos.api.exception.NacosException;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Properties;

@SpringBootApplication
public class CommonUtilsApplication {

    public static void main(String[] args) {
        SpringApplication.run(CommonUtilsApplication.class, args);
    }

    @Bean
    public ApplicationRunner applicationRunner(ConfigService configService) {
        return args -> {
            String[] submodules = {
                    "user-service",
                    "ocr-gateway",
                    "common-utils"

            };
            for (String submodule : submodules) {
                String dataId = submodule + "-dev.yml";
                String group = "ocr_back";
                String filePath = "common-utils/src/main/resources/ymls/" + dataId;
                String content = new String(Files.readAllBytes(Paths.get(filePath)), StandardCharsets.UTF_8);

                try {
                    boolean isPublishOk = configService.publishConfig(dataId, group, content);
                    if (isPublishOk) {
                        System.out.println(submodule + " 配置推送成功");
                    } else {
                        System.out.println(submodule + " 配置推送失败");
                    }
                } catch (NacosException e) {
                    e.printStackTrace();
                }
            }
        };
    }

    @Bean
    public ConfigService configService() throws NacosException {
        String serverAddr = "127.0.0.1:8848"; // Nacos 服务器地址
        Properties properties = new Properties();
        properties.put("serverAddr", serverAddr);
        return NacosFactory.createConfigService(properties);
    }

}
