package com.example.layout.controller;


import com.example.citybusiness.contract.model.LayoutGenerateRequest;
import com.example.citybusiness.contract.model.LayoutJson;
import com.example.citybusiness.contract.model.LayoutParams;
import com.example.citybusiness.contract.model.LayoutsListItem;
import com.example.layout.dto.*;

import com.example.layout.service.RabbitMQProducerService;
import com.example.layout.model.Jobs;
import com.example.layout.model.Layouts;

import com.example.layout.proto.CityMqContract;
import com.example.layout.service.IJobsService;
import com.example.layout.service.ILayoutsService;
import com.example.layout.utils.FileUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.authentication.AnonymousAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;
import java.io.IOException;
import java.util.UUID;
import com.example.layout.utils.Base62Util;
import java.util.List;

@RestController
@RequestMapping("/api/layout")
public class LayoutsController {

    private final RabbitMQProducerService rabbitMQProducerService;
    private final IJobsService jobsService;
    private final ILayoutsService layoutsService;
    private final ObjectMapper objectMapper;
    private final FileUtil fileUtil;

    public LayoutsController(RabbitMQProducerService rabbitMQProducerService, IJobsService jobsService, ILayoutsService layoutsService, ObjectMapper objectMapper, FileUtil fileUtil) {
        this.rabbitMQProducerService = rabbitMQProducerService;
        this.jobsService = jobsService;
        this.layoutsService = layoutsService;
        this.objectMapper = objectMapper;
        this.fileUtil = fileUtil;
    }

    // 1. 生成布局
    @PostMapping("/generate")
    public ResponseEntity<ApiResponse<ApiFieldResponse.LayoutIdResponse>> generateLayout(@RequestBody LayoutGenerateRequest request, @RequestHeader("Authorization") String authorizationHeader) {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            if (authentication != null && authentication.isAuthenticated()
                    && !(authentication instanceof AnonymousAuthenticationToken)
                    && authentication.getPrincipal() instanceof Long) {
                userId = (Long) authentication.getPrincipal();
            }
            if (userId == null) {
                ApiResponse<ApiFieldResponse.LayoutIdResponse> errorResponse = new ApiResponse<>(1, "用户未认证", null);
                return ResponseEntity.status(401).body(errorResponse);
            }
            String taskId = UUID.randomUUID().toString();
            long layoutId = Math.abs(UUID.randomUUID().getMostSignificantBits());
            Jobs job = new Jobs();
            job.setTaskId(taskId);
            job.setUserId(userId);
            job.setType("layout");
            // params 必须为有效 JSON 字符串
            String paramsJson = objectMapper.writeValueAsString(request.getParams());
            job.setPayloadJson(paramsJson);
            job.setStatus(0);
            job.setLayoutId(layoutId);
            jobsService.save(job);
            String layout_dir_path = "assets/" + userId + "/" + layoutId + "/";
            // 校验 responseMode 和 forceRegenerate
            String responseMode = request.getResponseMode() != null ? request.getResponseMode() : "default";
            boolean forceRegenerate = request.getForceRegenerate() != null ? request.getForceRegenerate() : false;
            // 构建proto消息
            CityMqContract.LayoutTaskMessage protoMsg = CityMqContract.LayoutTaskMessage.newBuilder()
                .setTaskId(taskId)
                .setType("layout")
                .setParams(paramsJson)
                .setLayoutDir(layout_dir_path)
                .setResponseMode(responseMode)
                .setForceRegenerate(forceRegenerate)
                .build();
            // 发布布局任务到 layout_task 队列
            rabbitMQProducerService.sendProtoMessage("city-exchange", "layout_task", protoMsg);
            ApiFieldResponse.LayoutIdResponse data = new ApiFieldResponse.LayoutIdResponse();
            data.setLayoutId(Base62Util.encode(layoutId));
            ApiResponse<ApiFieldResponse.LayoutIdResponse> response = new ApiResponse<>(0, "success", data);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.ErrorResponse error = new ApiFieldResponse.ErrorResponse();
            error.setMessage("生成布局失败: " + e.getMessage());
            return ResponseEntity.internalServerError().body(new ApiResponse<>(1, error.getMessage(), null));
        }
    }

    // 2. 查询任务进度（通过 layoutId 查询）
    @GetMapping("/progress/{layoutId}")
    public ResponseEntity<ApiFieldResponse.StatusResponse> getLayoutProgress(@PathVariable String layoutId) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getLayoutId, layoutIdLong).one();
            if (job == null) {
                ApiFieldResponse.StatusResponse response = new ApiFieldResponse.StatusResponse();
                response.setStatus(-1);
                response.setMessage("未找到任务");
                return ResponseEntity.ok(response);
            }
            ApiFieldResponse.StatusResponse response = new ApiFieldResponse.StatusResponse();
            response.setStatus(job.getStatus());
            response.setMessage("success");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.StatusResponse response = new ApiFieldResponse.StatusResponse();
            response.setStatus(-1);
            response.setMessage("查询进度失败: " + e.getMessage());
            return ResponseEntity.ok(response);
        }
    }

    // 新增：查询布局结果 返回实际的svg内容。
    @GetMapping("/result/{layoutId}")
    public ResponseEntity<ApiFieldResponse.LayoutResultResponse> getLayoutResult(@PathVariable String layoutId) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getLayoutId, layoutIdLong).eq(Jobs::getType, "layout").one();
            if (job == null) {
                ApiFieldResponse.LayoutResultResponse response = new ApiFieldResponse.LayoutResultResponse();
                response.setStatus(-1);
                response.setSvgContent(null);
                return ResponseEntity.ok(response);
            }
            Layouts layout = layoutsService.getById(layoutIdLong);
            if (layout == null) {
                ApiFieldResponse.LayoutResultResponse response = new ApiFieldResponse.LayoutResultResponse();
                response.setStatus(-1);
                response.setSvgContent(null);
                return ResponseEntity.ok(response);
            }
            String svgUrl = layout.getSvgUrl();
            String svgContent = layoutsService.readSvgContent(svgUrl);
            ApiFieldResponse.LayoutResultResponse response = new ApiFieldResponse.LayoutResultResponse();
            response.setSvgContent(svgContent); // 返回svg内容
            response.setLayoutParams(objectMapper.readValue(layout.getParamsJson(), LayoutParams.class));
            response.setStatus(job.getStatus());
            response.setLayoutId(Base62Util.encode(layout.getId()));
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.LayoutResultResponse response = new ApiFieldResponse.LayoutResultResponse();
            response.setStatus(-1);
            response.setSvgContent(null);
            return ResponseEntity.ok(response);
        }
    }

    // 5. 删除任务（通过 layoutId 删除）
    @DeleteMapping("/job/{layoutId}")
    public ResponseEntity<ApiFieldResponse.DeleteResponse> deleteJob(@PathVariable String layoutId) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Jobs job = jobsService.lambdaQuery().eq(Jobs::getLayoutId, layoutIdLong).eq(Jobs::getType, "layout").one();
            ApiFieldResponse.DeleteResponse response = new ApiFieldResponse.DeleteResponse();
            if (job == null) {
                response.setDeleted(false);
                return ResponseEntity.ok(response);
            }
            if (job.getStatus() != 2 && job.getStatus() != -1) {
                response.setDeleted(false);
                return ResponseEntity.ok(response);
            }
            jobsService.removeById(job.getId());
            response.setDeleted(true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.DeleteResponse response = new ApiFieldResponse.DeleteResponse();
            response.setDeleted(false);
            return ResponseEntity.ok(response);
        }
    }

    @DeleteMapping("/delete/{layoutId}")
    public ResponseEntity<ApiFieldResponse.DeleteResponse> deleteLayout(@PathVariable String layoutId) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Layouts layout = layoutsService.getById(layoutIdLong);
            ApiFieldResponse.DeleteResponse response = new ApiFieldResponse.DeleteResponse();
            if (layout == null) {
                response.setDeleted(false);
                return ResponseEntity.ok(response);
            }
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            if (authentication != null && authentication.isAuthenticated()
                    && !(authentication instanceof AnonymousAuthenticationToken)
                    && authentication.getPrincipal() instanceof Long) {
                userId = (Long) authentication.getPrincipal();
            }
            if (userId == null || !userId.equals(layout.getUserId())) {
                response.setDeleted(false);
                return ResponseEntity.ok(response);
            }
            // 逻辑删除：将status设为-1（不再限制status值，所有布局都可逻辑删除）
            layout.setStatus(-1);
            layoutsService.updateById(layout);
            response.setDeleted(true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.DeleteResponse response = new ApiFieldResponse.DeleteResponse();
            response.setDeleted(false);
            return ResponseEntity.ok(response);
        }
    }

    @PutMapping("/update/{layoutId}")
    public ResponseEntity<ApiFieldResponse.UpdateResponse> updateLayoutStatus(@PathVariable String layoutId, @RequestBody LayoutJson layoutJson) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Layouts layout = layoutsService.getById(layoutIdLong);
            ApiFieldResponse.UpdateResponse response = new ApiFieldResponse.UpdateResponse();
            if (layout == null) {
                response.setUpdated(false);
                return ResponseEntity.ok(response);
            }
            layoutsService.updateLayoutJsonContent(layout, layoutJson);
            response.setUpdated(true);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiFieldResponse.UpdateResponse response = new ApiFieldResponse.UpdateResponse();
            response.setUpdated(false);
            return ResponseEntity.ok(response);
        }
    }

    @GetMapping("list_layouts")
    public ResponseEntity<ApiResponse<List<LayoutsListItem>>> listUserLayouts() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            Long userId = null;
            if (authentication != null && authentication.isAuthenticated()
                    && !(authentication instanceof AnonymousAuthenticationToken)
                    && authentication.getPrincipal() instanceof Long) {
                userId = (Long) authentication.getPrincipal();
            }
            List<LayoutsListItem> layouts = layoutsService.listUserLayouts(userId);
            ApiResponse<List<LayoutsListItem>> response = new ApiResponse<>(0, "success", layouts);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiResponse<List<LayoutsListItem>> response = new ApiResponse<>(1, "查询失败: " + e.getMessage(), null);
            return ResponseEntity.ok(response);
        }
    }


    @GetMapping("/layout_json/{layoutId}")
    public ResponseEntity<ApiResponse<LayoutJson>> getLayoutJson(@PathVariable String layoutId) {
        try {
            Long layoutIdLong = Base62Util.decode(layoutId); // 解码Base62字符串为Long
            Layouts layout = layoutsService.getById(layoutIdLong);
            if (layout == null) {
                ApiResponse<LayoutJson> response = new ApiResponse<>(1, "布局未找到", null);
                return ResponseEntity.ok(response);
            }
            String layout_dir_path = "assets/" + layout.getUserId() + "/" + layout.getId() + "/";
            String layout_json_file_path = layout_dir_path + "layout.json";
            String layoutJsonContent = fileUtil.readFile(layout_json_file_path); // 实例调用
            if (layoutJsonContent.trim().isEmpty()) {
                ApiResponse<LayoutJson> response = new ApiResponse<>(1, "布局JSON文件不存在或为空", null);
                return ResponseEntity.ok(response);
            }
            LayoutJson layoutJson = objectMapper.readValue(layoutJsonContent, LayoutJson.class);
            ApiResponse<LayoutJson> response = new ApiResponse<>(0, "success", layoutJson);
            return ResponseEntity.ok(response);
        } catch (IOException e) {
            ApiResponse<LayoutJson> response = new ApiResponse<>(1, "读取布局JSON失败: " + e.getMessage(), null);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            ApiResponse<LayoutJson> response = new ApiResponse<>(1, "系统异常: " + e.getMessage(), null);
            return ResponseEntity.ok(response);
        }
    }
}
