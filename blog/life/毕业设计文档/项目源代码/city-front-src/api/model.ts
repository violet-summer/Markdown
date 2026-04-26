import type { ApiEnvelope } from "@/models/api-contract";
import type {
  GenerateModelRequest,
  GenerateModelResponse,
  GenerateModelProgressResponse,
  ListModelsResponse,
  ModelResultResponse,
} from "@/models/model-api";
import { apiRequest } from "./http";

/**
 * 生成 3D 模型。
 * POST /api/models/generate
 */
export function generateModel(payload: GenerateModelRequest) {
  return apiRequest<ApiEnvelope<GenerateModelResponse>>("/api/models/generate", {
    method: "POST",
    data: payload,
  });
}

/**
 * 查询模型生成进度。
 * GET /api/models/progress/{layoutId}
 */
export function getModelProgress(layoutId: string) {
  return apiRequest<ApiEnvelope<GenerateModelProgressResponse>>(`/api/models/progress/${layoutId}`, {
    method: "GET",
  });
}

/**
 * 获取模型生成结果。
 * GET /api/models/result/{layoutId}
 */
export function getModelResult(layoutId: string) {
  return apiRequest<ApiEnvelope<ModelResultResponse>>(`/api/models/result/${layoutId}`, {
    method: "GET",
  });
}

/**
 * 获取模型列表。
 * GET /api/models/list
 */
export function listModels() {
  return apiRequest<ApiEnvelope<ListModelsResponse> | ListModelsResponse>("/api/models/list");
}

/**
 * 根据 modelId 获取模型文件。
 * GET /api/models/model/{modelId}
 */
export function getModelFile(modelId: string) {
  return apiRequest<ApiEnvelope<ModelResultResponse> | ModelResultResponse>(`/api/models/model/${modelId}`);
}

/**
 * 获取模型场景信息。
 * GET /api/models/scene/{sceneId}
 */
export function getScene(sceneId: string) {
  return apiRequest<ApiEnvelope<Record<string, unknown>>>(`/api/models/scene/${sceneId}`);
}

/**
 * 删除模型。
 * DELETE /api/models/{modelId}
 */
export function deleteModel(modelId: number) {
  return apiRequest<ApiEnvelope<{ success: boolean }>>(`/api/models/${modelId}`, {
    method: "DELETE",
  });
}
