package com.example.layout.controller;

import com.example.citybusiness.contract.model.LayoutsListItem;
import com.example.citybusiness.contract.model.ModelGenerateRequest;
import com.example.citybusiness.contract.model.ModelListResponseDTO;
import com.example.layout.dto.ApiFieldResponse;
import com.example.layout.model.Models;
import com.example.layout.proto.CityMqContract;
import com.example.layout.service.IModelsService;
import com.example.layout.utils.Base62Util;
import io.minio.GetPresignedObjectUrlArgs;
import io.minio.MinioClient;
import io.minio.http.Method;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import com.example.layout.service.RabbitMQProducerService;
import org.springframework.beans.factory.annotation.Value;
import java.util.UUID;

import com.example.layout.service.IJobsService;
import com.example.layout.service.ILayoutsService;
import com.example.layout.model.Jobs;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;
import java.util.stream.Collectors;



@RestController
@RequestMapping("/api/models")
public class ModelsController {

    private final RabbitMQProducerService rabbitMQProducerService;
    private final IJobsService jobsService;
    private final ILayoutsService layoutsService;
    private final IModelsService modelsService;
    private final MinioClient minioClient;

    @Value("${minio.bucket}")
    private String minioBucket;

    @Value("${minio.app-prefix:app/}")
    private String minioAppPrefix;

    @Value("${minio.presign-expiry-seconds:3600}")
    private int presignExpirySeconds;

    public ModelsController(RabbitMQProducerService rabbitMQProducerService, ObjectMapper objectMapper, IJobsService jobsService, ILayoutsService layoutsService, IModelsService modelsService, MinioClient minioClient) {
        this.rabbitMQProducerService = rabbitMQProducerService;
        this.jobsService = jobsService;
        this.layoutsService = layoutsService;
        this.modelsService = modelsService;
        this.minioClient = minioClient;
    }

    // 生成3D模型
    @PostMapping("/generate")
    public ResponseEntity<ApiFieldResponse.StatusResponse> generate3DModel(@RequestBody ModelGenerateRequest request) {
        String taskId = UUID.randomUUID().toString();
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            if (authentication != null && authentication.isAuthenticated()
                    && !(authentication instanceof AnonymousAuthenticationToken)
                    && authentication.getPrincipal() instanceof Long) {
                userId = (Long) authentication.getPrincipal();
            }
            long layoutId = 0;
            if (request.getLayoutId() != null) {
                layoutId = Base62Util.decode(request.getLayoutId());
            }

            // 旧模型全部作废，保留历史记录
            modelsService.lambdaUpdate()
                    .eq(Models::getLayoutId, layoutId)
                    .ne(Models::getStatus, 3)
                    .set(Models::getStatus, 3)
                    .update();

            Jobs job = new Jobs();
            job.setTaskId(taskId);
            job.setUserId(userId);
            job.setType("model");
            // 不保存 layoutId 到 jobs.payload_json，避免 MySQL JSON 精度问题
            job.setPayloadJson("{}");
            job.setStatus(0);
            job.setLayoutId(layoutId);
            jobsService.save(job);

            String layoutJsonFilePath = "assets/" + userId + "/" + layoutId + "/layout.json";
            String modelsStoreDir = "assets/" + userId + "/" + layoutId + "/models/";
            // 用 proto 生成类构建消息
            CityMqContract.ModelTaskMessage protoMsg = CityMqContract.ModelTaskMessage.newBuilder()
                .setTaskId(taskId)
                .setType("model")
                .setOutputDir(modelsStoreDir)
                .setLayoutJsonFilePath(layoutJsonFilePath)
                .build();
            // 用 RabbitMQProducerService 发送 proto 二进制消息
            // 发布模型任务到 model_task 队列
            rabbitMQProducerService.sendProtoMessage("city-exchange", "model_task", protoMsg);

            ApiFieldResponse.StatusResponse response = new ApiFieldResponse.StatusResponse();
            response.setStatus(0);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.StatusResponse errorResponse = new ApiFieldResponse.StatusResponse();
            errorResponse.setStatus(-1);
            errorResponse.setMessage(e.getMessage());
            System.out.println("模型生成错误" + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    // 查询模型任务进度
    @GetMapping("/progress/{layoutId}")
    public ResponseEntity<ApiFieldResponse.StatusResponse> getModelProgress(@PathVariable String layoutId) {
        List<Jobs> jobs = jobsService.lambdaQuery()
                .eq(Jobs::getLayoutId, Base62Util.decode(layoutId))
                .eq(Jobs::getType, "model")
                .orderByDesc(Jobs::getId)
                .list();
        if (jobs == null || jobs.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        Jobs latestJob = jobs.stream()
                .filter(j -> j.getStatus() != null && j.getStatus() >= 0)
                .findFirst()
                .orElse(jobs.get(0));
        ApiFieldResponse.StatusResponse response = new ApiFieldResponse.StatusResponse();
        response.setStatus(latestJob.getStatus());
        return ResponseEntity.ok(response);
    }

    // 查询模型任务结果,返回模型id和对应glb文件预签名URL。
    @GetMapping("/result/{layoutId}")
    public ResponseEntity<ApiFieldResponse.ModelResultResponse> getModelResult(@PathVariable String layoutId) {
        List<Jobs> jobs = jobsService.lambdaQuery()
                .eq(Jobs::getLayoutId, Base62Util.decode(layoutId))
                .eq(Jobs::getType, "model")
                .orderByDesc(Jobs::getId)
                .list();
        if (jobs == null || jobs.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        Jobs latestJob = jobs.get(0);
        List<ApiFieldResponse.ModelFileInfo> modelFiles = new java.util.ArrayList<>();
        Long layoutIdLong = Base62Util.decode(layoutId);
        List<Models> models = modelsService.lambdaQuery()
                .eq(Models::getLayoutId, layoutIdLong)
                .ne(Models::getStatus, 3)
                .orderByDesc(Models::getId)
                .list();

        for (Models model : models) {
            String modelId = Base62Util.encode(model.getId());
            String relativePath = model.getObjUrl();
            if (relativePath == null || relativePath.isBlank()) {
                continue;
            }
            String objectName = toMinioObjectName(relativePath);
            String presignedUrl;
            try {
                presignedUrl = minioClient.getPresignedObjectUrl(
                        GetPresignedObjectUrlArgs.builder()
                                .method(Method.GET)
                                .bucket(minioBucket)
                                .object(objectName)
                                .expiry(presignExpirySeconds)
                                .build()
                );
            } catch (Exception e) {
                presignedUrl = "";
            }
            modelFiles.add(new ApiFieldResponse.ModelFileInfo(modelId, presignedUrl));
        }
        ApiFieldResponse.ModelResultResponse response = new ApiFieldResponse.ModelResultResponse();
        response.setStatus(latestJob.getStatus());
        response.setModels(modelFiles);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/list")
    public ResponseEntity<ApiFieldResponse.ModelsListResponse> listModels() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            if (authentication != null && authentication.isAuthenticated()
                    && !(authentication instanceof AnonymousAuthenticationToken)
                    && authentication.getPrincipal() instanceof Long) {
                userId = (Long) authentication.getPrincipal();
            }
            List<LayoutsListItem> layouts = layoutsService.listUserLayouts(userId);
            List<ApiFieldResponse.LayoutWithModels> layoutWithModelsList = layouts.stream().map(layout -> {
                Long layoutId = null;
                try {
                    if (layout.getLayoutId() != null) {
                        layoutId = Base62Util.decode(layout.getLayoutId());
                    }
                } catch (Exception e) {
                    try {
                        if (layout.getLayoutId() != null) {
                            layoutId = Long.valueOf(layout.getLayoutId());
                        }
                    } catch (Exception ignore) {
                    }
                }

                // 每个布局返回所有未作废模型(status != 3)
                List<Models> layoutModels = (layoutId != null) ? modelsService.lambdaQuery()
                        .eq(Models::getLayoutId, layoutId)
                        .ne(Models::getStatus, 3)
                        .orderByDesc(Models::getId)
                        .list() : java.util.Collections.emptyList();

                List<ModelListResponseDTO> models = layoutModels.stream().map(entity -> {
                    ModelListResponseDTO dto = new ModelListResponseDTO();
                    dto.setModelId(Base62Util.encode(entity.getId()));
                    dto.setModelName("未命名");
                    dto.setStatus(entity.getStatus());
                    return dto;
                }).collect(Collectors.toList());
                return new ApiFieldResponse.LayoutWithModels(layout, models);
            }).collect(Collectors.toList());
            ApiFieldResponse.ModelsListResponse response = new ApiFieldResponse.ModelsListResponse();
            response.setLayoutWithModelsList(layoutWithModelsList);
            response.setMessage("success");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.ModelsListResponse errorResponse = new ApiFieldResponse.ModelsListResponse();
            errorResponse.setMessage("查询失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(errorResponse);
        }
    }

    @GetMapping("/model/{modelId}")
    public ResponseEntity<ApiFieldResponse.ModelSingleResponse> getModelIdMap(@PathVariable String modelId) {
        try {
            Long modelIdLong = Base62Util.decode(modelId);
            Models model = modelsService.getById(modelIdLong);
            if (model == null || (model.getStatus() != null && model.getStatus() == 3)) {
                ApiFieldResponse.ModelSingleResponse response = new ApiFieldResponse.ModelSingleResponse();
                response.setStatus(-1);
                response.setModel(null);
                return ResponseEntity.status(404).body(response);
            }
            String relativePath = model.getObjUrl();
            if (relativePath == null || relativePath.isBlank()) {
                ApiFieldResponse.ModelSingleResponse response = new ApiFieldResponse.ModelSingleResponse();
                response.setStatus(-1);
                response.setModel(null);
                return ResponseEntity.status(404).body(response);
            }
            String objectName = toMinioObjectName(relativePath);
            String presignedUrl = minioClient.getPresignedObjectUrl(
                    GetPresignedObjectUrlArgs.builder()
                            .method(Method.GET)
                            .bucket(minioBucket)
                            .object(objectName)
                            .expiry(presignExpirySeconds)
                            .build()
            );
            ApiFieldResponse.ModelFileInfo fileInfo = new ApiFieldResponse.ModelFileInfo(modelId, presignedUrl);
            ApiFieldResponse.ModelSingleResponse response = new ApiFieldResponse.ModelSingleResponse();
            response.setStatus(0);
            response.setModel(fileInfo);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.ModelSingleResponse response = new ApiFieldResponse.ModelSingleResponse();
            response.setStatus(-1);
            response.setModel(null);
            System.out.println("获取模型错误" + e.getMessage());
            return ResponseEntity.status(500).body(response);
        }
    }

    private String toMinioObjectName(String relativePath) {
        String cleanPath = relativePath == null ? "" : relativePath.trim();
        if (cleanPath.isEmpty()) {
            return "";
        }

        String minioScheme = "minio://";
        if (cleanPath.startsWith(minioScheme)) {
            String withoutScheme = cleanPath.substring(minioScheme.length());
            int firstSlash = withoutScheme.indexOf('/');
            if (firstSlash >= 0 && firstSlash + 1 < withoutScheme.length()) {
                String objectPath = withoutScheme.substring(firstSlash + 1);
                if (objectPath.startsWith("/")) {
                    objectPath = objectPath.substring(1);
                }
                return objectPath;
            }
            return "";
        }

        if (cleanPath.startsWith("/")) {
            cleanPath = cleanPath.substring(1);
        }
        String prefix = minioAppPrefix == null ? "" : minioAppPrefix.trim();
        if (!prefix.isEmpty() && !prefix.endsWith("/")) {
            prefix = prefix + "/";
        }
        if (cleanPath.startsWith(prefix)) {
            return cleanPath;
        }
        return prefix + cleanPath;
    }
}
