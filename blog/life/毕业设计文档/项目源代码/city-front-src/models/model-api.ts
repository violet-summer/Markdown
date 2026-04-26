/** 生成 3D 模型请求体。 */
export interface GenerateModelRequest {
    force_regenerate?: boolean;
    layout_id?: string;
    response_mode?: string;
    [property: string]: any;
}
/**
 * ResponseEntityStatusResponse
 */
// 只是发送请求时的状态，真正的生成状态需要通过查询接口获取。0成功，-1失败，2处理中
export interface GenerateModelResponse {
    message?: string;
    status?: number;
    [property: string]: any;
}

/** 生成进度响应结构。 */
export interface GenerateModelProgressResponse {
  message?: string;
  status?: number;
  [property: string]: any;
}

export interface ModelFileInfo {
  modelId?: string;
  objContent?: string;
  objPath?: string;
  [property: string]: any;
}

export interface ModelResultResponse {
  models?: ModelFileInfo[];
  status?: number;
  [property: string]: any;
}

export interface LayoutsListItem {
  layout_id?: string;
  layout_name?: string;
  status?: number;
  svg_url?: string;
  [property: string]: any;
}

export interface ModelListResponseDTO {
  model_id?: string;
  model_name?: string;
  status?: number;
  [property: string]: any;
}

export interface LayoutWithModels {
  layout?: LayoutsListItem;
  models?: ModelListResponseDTO[];
  [property: string]: any;
}

export interface ListModelsResponse {
  layout_with_models_list?: LayoutWithModels[];
  message?: string;
  [property: string]: any;
}

/** 生成模型返回结构（URL 或内联内容）。 */
export type ModelGenerateResponse = {
  modelId: string;
  objUrl?: string;
  mtlUrl?: string;
  objContent?: string;
  mtlContent?: string;
  status?: number;
};

/** 模型列表项。 */
export type ModelSummary = {
  modelId: string;
  layout_id: string;
  objUrl: string;
  mtlUrl: string;
  status: number;
};

/** 模型详情结构，当前与列表项一致。 */
export type ModelDetail = ModelSummary;
