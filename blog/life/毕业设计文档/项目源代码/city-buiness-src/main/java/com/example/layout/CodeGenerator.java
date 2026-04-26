package com.example.layout;

import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;

import java.util.Collections;

public class CodeGenerator {
    public static void main(String[] args) {
        FastAutoGenerator.create(
                        "jdbc:mysql://localhost:3306/3d_city?useUnicode=true&useSSL=false&characterEncoding=utf8&serverTimezone=Asia/Shanghai",
                        "root",
                        "helloworld"
                )
                .globalConfig(builder -> {
                    builder.author("city_business")
                            .outputDir(System.getProperty("user.dir") + "/src/main/java")
                            .disableOpenDir();
                })
                .packageConfig(builder -> {
                    builder.parent("com.example.citybusiness")
                            .pathInfo(Collections.singletonMap(OutputFile.xml, System.getProperty("user.dir") + "/src/main/resources/mapper"))
                            .entity("model")                   // entity类生成到 model 子包
                            .mapper("mapper")                  // mapper接口生成到 mapper 子包
                            .service("service")                // service生成到 service 子包
                            .serviceImpl("service.impl")       // serviceImpl生成到 service.impl 子包
                            .controller("controller");      // controller生成到 controller 子包
                })
                .strategyConfig(builder -> {
                    builder.addInclude("users", "jobs", "layouts", "models", "sessions") // 指定表名
                            .entityBuilder().enableFileOverride().enableLombok().enableFileOverride()
                            .mapperBuilder().enableFileOverride()
                            .serviceBuilder()
                            .controllerBuilder();
                })
                .execute();
    }
}
