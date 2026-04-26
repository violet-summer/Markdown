import type { ApiResponseMode } from "@/models/api-contract";
import type { LayoutGenerateRequest } from "@/models/layout-generate-request";
import type { LayoutResultResponse, LayoutsListItem } from "@/models/layout-result";
import { BigParksPolygon, BlocksPolygon, CoastlinePolygon, DividedBuildingsPolygons, GroundPolygon, LayoutJson, MainExteriorInteriorRoadPolygon, MainNormalRoadPolygon, MajorExteriorInteriorRoadPolygon, MajorNormalRoadPolygon, MinorExteriorInteriorRoadPolygon, MinorNormalRoadPolygon, Origin, PolygonsToProcess, SeaPolygon, WaterRoadPolygon, WaterSecondaryRoadPolygon, WiverPolygon, WorldDimensions } from "./layout-update";

export type { LayoutResultResponse, LayoutsListItem };

/** 生成布局后返回的布局标识。 */
export type LayoutIdResponse = {
  layout_id: string;
};

/** 布局生成任务进度查询响应。 */
export type LayoutProgressResponse = {
  phase?: string;
  progress?: number;
  status?: number | string;
  data?: LayoutResultResponse;
  error?: string;
};

/** 布局附属编辑数据（流线与多边形）。 */
export interface LayoutArtifactsResponse{
    code?: number;
    data?: LayoutJson;
    message?: string;
    [property: string]: any;
}

/** 保存 SVG 接口请求体。 */
export type SaveLayoutRequest = {
  layoutId: number;
  svgContent: string;
  responseMode?: ApiResponseMode;
};

/** 保存可见图层编辑结果请求体。 */
export type SaveLayoutEditRequest = {
  layoutId: number;
  layerVisibility: Record<string, boolean>;
  responseMode?: ApiResponseMode;
};


/** 保存流线/多边形 artifacts 请求体。 */
export interface SaveLayoutArtifactsRequest {
    big_parks_polygon?: Array<BigParksPolygon[]>;
    blocks_polygon?: Array<BlocksPolygon[]>;
    coastline_polygon?: CoastlinePolygon[];
    divided_buildings_polygons?: Array<DividedBuildingsPolygons[]>;
    ground_polygon?: GroundPolygon[];
    main_exterior_interior_road_polygon?: MainExteriorInteriorRoadPolygon[];
    main_normal_road_polygon?: Array<MainNormalRoadPolygon[]>;
    major_exterior_interior_road_polygon?: MajorExteriorInteriorRoadPolygon[];
    major_normal_road_polygon?: Array<MajorNormalRoadPolygon[]>;
    minor_exterior_interior_road_polygon?: MinorExteriorInteriorRoadPolygon[];
    minor_normal_road_polygon?: Array<MinorNormalRoadPolygon[]>;
    origin?: Origin;
    polygons_to_process?: Array<PolygonsToProcess[]>;
    river_polygon?: WiverPolygon[];
    sea_polygon?: SeaPolygon[];
    secondary_road_polygon?: string;
    small_parks_polygons?: string[];
    water_road_polygon?: Array<WaterRoadPolygon[]>;
    water_secondary_road_polygon?: WaterSecondaryRoadPolygon[];
    world_dimensions?: WorldDimensions;
    [property: string]: any;
}

  export interface SaveLayoutArtifactsResponse {
    updated?: boolean;
    [property: string]: any;
  }


/** 保存布局后的返回结构。 */
export type LayoutSaveResponse = {
  layout_id: string;
  svg_content?: string;
  svgUrl?: string;
};

/** 生成布局请求体（复用 LayoutGenerateRequest）。 */
export type GenerateLayoutRequest = LayoutGenerateRequest;

/** 布局列表响应体（数组）。 */
export type ListLayoutsResponse = LayoutsListItem[];
