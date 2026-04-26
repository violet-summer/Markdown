import type { ApiEnvelope } from '@/models/api-contract';
import type {
  GenerateLayoutRequest,
  LayoutArtifactsResponse,
  LayoutIdResponse,
  LayoutProgressResponse,
  LayoutResultResponse,
  LayoutSaveResponse,
  SaveLayoutArtifactsResponse,
  ListLayoutsResponse,
  SaveLayoutArtifactsRequest,
  SaveLayoutEditRequest,
  SaveLayoutRequest,
} from '@/models/layout-api';
import { apiRequest } from './http';
export type { LayoutIdResponse };

/**
 * 发起布局生成。
 * POST /api/layout/generate
 */
export function generateLayout(payload: GenerateLayoutRequest): Promise<ApiEnvelope<LayoutIdResponse>> {
  return apiRequest('/api/layout/generate', {
    method: 'POST',
    data: payload,
  });
}

/**
 * 查询布局生成进度。
 * GET /api/layout/progress/{layoutId}
 */
export function getLayoutProgress(layoutId: string) {
  return apiRequest<ApiEnvelope<LayoutProgressResponse>>(`/api/layout/progress/${layoutId}`, {
    method: 'GET',
  });
}

/**
 * 获取布局列表。
 * GET /api/layout/list_layouts
 */
export function listLayouts() {
  return apiRequest<ApiEnvelope<ListLayoutsResponse>>('/api/layout/list_layouts');
}

/**
 * 获取布局结果（含 SVG、参数等）。
 * GET /api/layout/result/{layoutId}
 */
export function getLayout(layoutId: string | number) {
  return apiRequest<ApiEnvelope<LayoutResultResponse>>(`/api/layout/result/${layoutId}`);
}

/**
 * 获取布局 JSON（用于要素编辑）。
 * GET /api/layout/layout_json/{layoutId}
 */
export function getLayoutJson(layoutId: string | number) {
  return apiRequest<LayoutArtifactsResponse | ApiEnvelope<LayoutArtifactsResponse>>(`/api/layout/layout_json/${layoutId}`);
}

/**
 * 获取布局附属编辑数据（streamlines/polygons）。
 * GET /api/layout/{layoutId}/artifacts
 */
export function getLayoutArtifacts(layoutId: number) {
  return apiRequest<ApiEnvelope<LayoutArtifactsResponse>>(`/api/layout/${layoutId}/artifacts`);
}

/**
 * 保存 SVG。
 * POST /api/layout/save
 */
export function saveLayout(payload: SaveLayoutRequest) {
  return apiRequest<ApiEnvelope<LayoutSaveResponse>>('/api/layout/save', {
    method: 'PUT',
    data: payload,
  });
}

/**
 * 保存布局附属编辑数据。
 * POST /api/layout/update/{layoutId}
 */
export function saveLayoutArtifacts(
  layoutId: string | number,
  payload: SaveLayoutArtifactsRequest
) {
  return apiRequest<ApiEnvelope<SaveLayoutArtifactsResponse>>(`/api/layout/update/${layoutId}`, {
    method: 'PUT',
    data: payload,
  });
}

/**
 * 保存图层可见性编辑结果。
 * POST /api/layout/{layoutId}/save-edit
 */
export function saveLayoutEdit(
  layoutId: number,
  payload: SaveLayoutEditRequest
) {
  return apiRequest<ApiEnvelope<LayoutSaveResponse>>(`/api/layout/${layoutId}/save-edit`, {
    method: 'POST',
    data: payload,
  });
}

/**
 * 由布局触发 3D 模型生成。
 * POST /api/layout/{layoutId}/generate-3d
 */
export function generate3DModel(layoutId: string | number) {
  return apiRequest<ApiEnvelope<{ modelId?: number; objUrl?: string; status?: number }>>(`/api/layout/${layoutId}/generate-3d`, {
    method: 'POST',
  });
}

/**
 * 删除布局。
 * DELETE /api/layout/delete/{layoutId}
 */
export function deleteLayout(layoutId : string | number) {
  return apiRequest<ApiEnvelope<{ success: boolean }>>(`/api/layout/delete/${layoutId}`, {
    method: 'DELETE',
  });
}
