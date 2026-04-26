package com.example.layout.utils;

import io.minio.MinioClient;
import io.minio.GetObjectArgs;
import io.minio.PutObjectArgs;
import io.minio.RemoveObjectArgs;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import java.io.IOException;

//提供基本的文件操作功能，如读取、写入、删除文件等。并这里保存文件目录的根路径，方便其他类调用。
//其它地方只需要传入相对路径即可
@Component
public class FileUtil {
    private final MinioClient minioClient;
    @Value("${minio.bucket}")
    private String bucket;
    @Value("${minio.app-prefix:app/}")
    private String appPrefix;

    public FileUtil(MinioClient minioClient) {
        this.minioClient = minioClient;
    }

    public String readFile(String relativePath) throws IOException {
        String objectName = buildObjectName(relativePath);
        try (var stream = minioClient.getObject(
                GetObjectArgs.builder()
                        .bucket(bucket)
                        .object(objectName)
                        .build())) {
            String content = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
            if (content == null || content.trim().isEmpty()) {
                return "文件内容为空：" + objectName;
            }
            return content;
        } catch (Exception e) {
            return "文件不存在或读取失败：" + objectName;
        }
}


    public void writeFile(String relativePath, String content) throws IOException {
        String objectName = buildObjectName(relativePath);
        try (var bais = new ByteArrayInputStream(content.getBytes(StandardCharsets.UTF_8))) {
            minioClient.putObject(
                    PutObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .stream(bais, content.length(), -1)
                            .contentType("text/plain")
                            .build()
            );
        } catch (Exception e) {
            throw new IOException("MinIO写入失败: " + objectName, e);
        }
    }

    public void deleteFile(String relativePath) throws IOException {
        String objectName = buildObjectName(relativePath);
        try {
            minioClient.removeObject(
                    RemoveObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectName)
                            .build()
            );
        } catch (Exception e) {
            throw new IOException("MinIO删除失败: " + objectName, e);
        }
    }
    private String buildObjectName(String relativePath) {
        String clean = relativePath == null ? "" : relativePath.trim();
        clean = clean.replace("\\", "/"); // 自动将反斜杠转为正斜杠
        if (clean.startsWith("/")) clean = clean.substring(1);
        String prefix = appPrefix == null ? "" : appPrefix.trim();
        if (!prefix.isEmpty() && !prefix.endsWith("/")) prefix += "/";
        return prefix + clean;
    }
}
