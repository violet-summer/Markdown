import type { ApiEnvelope } from "@/models/api-contract";
import type {
  LayoutArtifactsResponse,
  LayoutProgressResponse,
  LayoutResultResponse,
  SaveLayoutArtifactsRequest,
  LayoutsListItem,
} from "@/models/layout-api";
import type { LayoutJson } from "@/models/layout-update";

type Point = { x: number; y: number };

export function unwrapEnvelope<T>(payload: ApiEnvelope<T> | T | null | undefined): T | null {
  if (!payload) {
    return null;
  }

  if (typeof payload === "object" && "data" in (payload as Record<string, unknown>)) {
    return ((payload as ApiEnvelope<T>).data ?? null) as T | null;
  }

  return payload as T;
}

export function normalizeLayouts(payload: ApiEnvelope<LayoutsListItem[]> | LayoutsListItem[] | null | undefined) {
  return unwrapEnvelope(payload) ?? [];
}

export function normalizeLayoutResult(
  payload: ApiEnvelope<LayoutResultResponse> | LayoutResultResponse | null | undefined
): LayoutResultResponse | null {
  return unwrapEnvelope(payload);
}

export function normalizeLayoutArtifacts(
  payload: ApiEnvelope<LayoutArtifactsResponse> | LayoutArtifactsResponse | null | undefined
): LayoutArtifactsResponse {
  return unwrapEnvelope(payload) ?? {};
}

export function normalizeLayoutProgress(
  payload: ApiEnvelope<LayoutProgressResponse> | LayoutProgressResponse | null | undefined
): LayoutProgressResponse {
  return unwrapEnvelope(payload) ?? {};
}

export function normalizeLayoutJson(
  payload: ApiEnvelope<LayoutArtifactsResponse> | LayoutArtifactsResponse | LayoutJson | null | undefined
): LayoutJson | null {
  if (!payload || typeof payload !== "object") {
    return null;
  }

  const candidate = payload as Record<string, unknown>;

  if (
    "ground_polygon" in candidate ||
    "blocks_polygon" in candidate ||
    "main_normal_road_polygon" in candidate
  ) {
    return candidate as LayoutJson;
  }

  const firstLayer = candidate.data as Record<string, unknown> | undefined;
  if (firstLayer && typeof firstLayer === "object") {
    if (
      "ground_polygon" in firstLayer ||
      "blocks_polygon" in firstLayer ||
      "main_normal_road_polygon" in firstLayer
    ) {
      return firstLayer as LayoutJson;
    }

    const secondLayer = firstLayer.data as Record<string, unknown> | undefined;
    if (
      secondLayer &&
      ("ground_polygon" in secondLayer ||
        "blocks_polygon" in secondLayer ||
        "main_normal_road_polygon" in secondLayer)
    ) {
      return secondLayer as LayoutJson;
    }
  }

  return null;
}

function toPoint(value: unknown): Point | null {
  if (!value || typeof value !== "object") {
    return null;
  }
  const candidate = value as Record<string, unknown>;
  const x = Number(candidate.x);
  const y = Number(candidate.y);
  if (!Number.isFinite(x) || !Number.isFinite(y)) {
    return null;
  }
  return { x, y };
}

function normalizePath(value: unknown): Point[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => toPoint(item))
    .filter((item): item is Point => item !== null);
}

function normalizePathGroups(value: unknown): Point[][] {
  if (!Array.isArray(value) || value.length === 0) {
    return [];
  }

  if (Array.isArray(value[0])) {
    return value
      .map((group) => normalizePath(group))
      .filter((group) => group.length > 0);
  }

  const single = normalizePath(value);
  return single.length > 0 ? [single] : [];
}

function normalizeExteriorInteriorPaths(value: unknown): Point[][] {
  if (!Array.isArray(value)) {
    return [];
  }

  const paths: Point[][] = [];
  value.forEach((item) => {
    if (!item || typeof item !== "object") {
      return;
    }
    const candidate = item as Record<string, unknown>;
    const exterior = normalizePath(candidate.exterior);
    const interior = normalizePath(candidate.interior);
    if (exterior.length > 0) {
      paths.push(exterior);
    }
    if (interior.length > 0) {
      paths.push(interior);
    }
  });

  return paths;
}

export function mapLayoutJsonToArtifacts(layoutJson: LayoutJson | null | undefined): Record<string, unknown> {
  if (!layoutJson) {
    return {};
  }

  return {
    bigParksPolygon: normalizePathGroups(layoutJson.big_parks_polygon),
    blocksPolygon: normalizePathGroups(layoutJson.blocks_polygon),
    coastlinePolygon: normalizePath(layoutJson.coastline_polygon),
    dividedBuildingsPolygons: normalizePathGroups(layoutJson.divided_buildings_polygons),
    groundPolygon: normalizePath(layoutJson.ground_polygon),
    mainExteriorInteriorRoadPolygon: normalizeExteriorInteriorPaths(layoutJson.main_exterior_interior_road_polygon),
    mainNormalRoadPolygon: normalizePathGroups(layoutJson.main_normal_road_polygon),
    majorExteriorInteriorRoadPolygon: normalizeExteriorInteriorPaths(layoutJson.major_exterior_interior_road_polygon),
    majorNormalRoadPolygon: normalizePathGroups(layoutJson.major_normal_road_polygon),
    minorExteriorInteriorRoadPolygon: normalizeExteriorInteriorPaths(layoutJson.minor_exterior_interior_road_polygon),
    minorNormalRoadPolygon: normalizePathGroups(layoutJson.minor_normal_road_polygon),
    polygonsToProcess: normalizePathGroups(layoutJson.polygons_to_process),
    riverPolygon: normalizePath(layoutJson.river_polygon),
    seaPolygon: normalizePath(layoutJson.sea_polygon),
    waterRoadPolygon: normalizePathGroups(layoutJson.water_road_polygon),
    waterSecondaryRoadPolygon: normalizePath(layoutJson.water_secondary_road_polygon),
    origin: {
      x: Number(layoutJson.origin?.x ?? 0),
      y: Number(layoutJson.origin?.y ?? 0),
    },
    worldDimensions: {
      x: Number(layoutJson.world_dimensions?.x ?? 100),
      y: Number(layoutJson.world_dimensions?.y ?? 100),
    },
    secondaryRoadPolygon: layoutJson.secondary_road_polygon ?? "",
    smallParksPolygons: layoutJson.small_parks_polygons ?? [],
  };
}

function toPointArray(value: unknown): Point[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => toPoint(item))
    .filter((item): item is Point => item !== null);
}

function toPointGroupArray(value: unknown): Point[][] {
  if (!Array.isArray(value)) {
    return [];
  }

  if (value.length === 0) {
    return [];
  }

  if (Array.isArray(value[0])) {
    return value
      .map((group) => toPointArray(group))
      .filter((group) => group.length > 0);
  }

  if (toPointArray(value).length > 0) {
    return [toPointArray(value)];
  }

  return [];
}

function toExteriorInteriorGroup(value: unknown) {
  if (!Array.isArray(value)) {
    return [];
  }

  const asPairObjects = value.every((item) => {
    if (!item || typeof item !== "object") {
      return false;
    }
    const candidate = item as Record<string, unknown>;
    return "exterior" in candidate || "interior" in candidate;
  });

  if (asPairObjects) {
    return value
      .map((item) => {
        const candidate = item as Record<string, unknown>;
        return {
          exterior: toPointArray(candidate.exterior),
          interior: toPointArray(candidate.interior),
        };
      })
      .filter((pair) => pair.exterior.length > 0 || pair.interior.length > 0);
  }

  const paths = toPointGroupArray(value);
  const pairs: Array<{ exterior: Point[]; interior: Point[] }> = [];
  for (let index = 0; index < paths.length; index += 2) {
    pairs.push({
      exterior: paths[index] ?? [],
      interior: paths[index + 1] ?? [],
    });
  }
  return pairs.filter((pair) => pair.exterior.length > 0 || pair.interior.length > 0);
}

export function mapArtifactsToSaveRequest(artifactsData: Record<string, any> | null | undefined): SaveLayoutArtifactsRequest {
  const source = artifactsData ?? {};

  return {
    big_parks_polygon: toPointGroupArray(source.bigParksPolygon),
    blocks_polygon: toPointGroupArray(source.blocksPolygon),
    coastline_polygon: toPointArray(source.coastlinePolygon),
    divided_buildings_polygons: toPointGroupArray(source.dividedBuildingsPolygons),
    ground_polygon: toPointArray(source.groundPolygon),
    main_exterior_interior_road_polygon: toExteriorInteriorGroup(source.mainExteriorInteriorRoadPolygon),
    main_normal_road_polygon: toPointGroupArray(source.mainNormalRoadPolygon),
    major_exterior_interior_road_polygon: toExteriorInteriorGroup(source.majorExteriorInteriorRoadPolygon),
    major_normal_road_polygon: toPointGroupArray(source.majorNormalRoadPolygon),
    minor_exterior_interior_road_polygon: toExteriorInteriorGroup(source.minorExteriorInteriorRoadPolygon),
    minor_normal_road_polygon: toPointGroupArray(source.minorNormalRoadPolygon),
    origin: {
      x: Number(source?.origin?.x ?? 0),
      y: Number(source?.origin?.y ?? 0),
    },
    polygons_to_process: toPointGroupArray(source.polygonsToProcess),
    river_polygon: toPointArray(source.riverPolygon),
    sea_polygon: toPointArray(source.seaPolygon),
    secondary_road_polygon: typeof source.secondaryRoadPolygon === "string" ? source.secondaryRoadPolygon : "",
    small_parks_polygons: Array.isArray(source.smallParksPolygons) ? source.smallParksPolygons : [],
    water_road_polygon: toPointGroupArray(source.waterRoadPolygon),
    water_secondary_road_polygon: toPointArray(source.waterSecondaryRoadPolygon),
    world_dimensions: {
      x: Number(source?.worldDimensions?.x ?? 100),
      y: Number(source?.worldDimensions?.y ?? 100),
    },
  };
}

export function readLayoutId(result: LayoutResultResponse | null | undefined): string | null {
  const rawId = result?.layout_id ?? (result as Record<string, unknown> | undefined)?.layoutId;
  if (rawId === null || typeof rawId === "undefined") {
    return null;
  }
  return String(rawId);
}

export function readSvgContent(result: LayoutResultResponse | null | undefined): string {
  return (result?.svg_content ?? (result as Record<string, unknown> | undefined)?.svgContent ?? "") as string;
}

export function readSvgUrl(result: LayoutResultResponse | null | undefined): string {
  return (result?.svg_url ?? (result as Record<string, unknown> | undefined)?.svgUrl ?? "") as string;
}

export function normalizeGenerateLayoutId(
  payload: ApiEnvelope<{ layout_id?: string | number }> | { layout_id?: string | number } | null | undefined
): string | null {
  const data = unwrapEnvelope(payload);
  const rawId = data?.layout_id;
  if (rawId === null || typeof rawId === "undefined") {
    return null;
  }
  return String(rawId);
}
