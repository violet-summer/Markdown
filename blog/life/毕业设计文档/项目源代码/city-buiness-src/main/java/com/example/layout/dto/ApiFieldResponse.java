package com.example.layout.dto;

import com.example.citybusiness.contract.model.LayoutParams;
import com.example.citybusiness.contract.model.LayoutsListItem;
import com.example.citybusiness.contract.model.ModelListResponseDTO;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;


@Data
public class ApiFieldResponse {

    @Data
    public static class StatusResponse {

        private Integer status;
        private String message = "null";
    }

    // 新增：查询布局结果
    @Data
    public static class LayoutResultResponse {

        Integer status;
        @JsonProperty("svg_content")
        String svgContent;
//        布局参数也要回写，便于前端复现参数。
        @JsonProperty("params")
LayoutParams layoutParams;

        @JsonProperty("layout_id")
        String layoutId;
    }

    // 新增：删除响应
    @Data
    public static class DeleteResponse {

        private boolean deleted;
    }

    // 新增：更新响应
    @Data
    public static class UpdateResponse {

        private boolean updated;
    }

    // 新增：模型ID映射结构
    @Data
    public static class ModelIdMapResult {

        @JsonProperty("model_ids")
        private java.util.Map<String, Long> modelIds;
    }

    // 新增：布局ID响应结构
    @Data
    public static class LayoutIdResponse {

        @JsonProperty("layout_id")
        private String layoutId; // base62编码字符串，手动赋值
    }

    // 新增：错误响应结构
    @Data
    public static class ErrorResponse {

        private String message;
    }

    // 布局及其模型列表结构
    @Data
    public static class LayoutWithModels {

        private LayoutsListItem layout;
        private java.util.List<ModelListResponseDTO> models;

        public LayoutWithModels(LayoutsListItem layout, java.util.List<ModelListResponseDTO> models) {
            this.layout = layout;
            this.models = models;
        }
    }

    // 布局-模型列表响应
    @Data
    public static class ModelsListResponse {

        @JsonProperty("layout_with_models_list")
        private java.util.List<LayoutWithModels> layoutWithModelsList;
        private String message;
    }

    // 新增：模型结果响应
    @Data
    public static class ModelResultResponse {

        private Integer status;
        private java.util.List<ModelFileInfo> models;

    }

    // 新增：单个模型结果响应
    @Data
    public static class ModelSingleResponse {

        private Integer status;
        @JsonProperty("model")
        private ModelFileInfo model;
    }

    // 新增：模型文件信息
    @Data
    public static class ModelFileInfo {

        @JsonProperty("model_id")
        private String modelId;
        @JsonProperty("presigned_url")
        private String presignedUrl;

        public ModelFileInfo(String modelId, String presignedUrl) {
            this.modelId = modelId;
            this.presignedUrl = presignedUrl;
        }

    }
}
