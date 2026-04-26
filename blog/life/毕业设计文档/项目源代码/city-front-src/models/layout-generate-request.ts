/**
 * 布局生成请求参数总定义。
 * 该文件用于约束 /api/layout/generate 的 request body 结构。
 */
/**
 * LayoutGenerateRequest
 */
export interface LayoutGenerateRequest {
    force_regenerate: boolean;
    params: LayoutParams;
    response_mode: string;
    
}

/**
 * LayoutParams
 */
export interface LayoutParams {
    download: DownloadConfig;
    map: MapConfig;
    options: OptionsConfig;
    origin: Origin;
    park_polygons: ParkPolygonsConfig;
    style: StyleConfig;
    tensor_field: TensorField;
    world_dimensions: WorldDimensions;
    zoom: number;
    
}

/**
 * DownloadConfig
 */
export interface DownloadConfig {
    image_scale: number;
    type: string;
    
}

/**
 * MapConfig
 */
export interface MapConfig {
    animate: boolean;
    animate_speed: number;
    buildings: BuildingsConfig;
    main: RoadConfig;
    major: RoadConfig;
    minor: RoadConfig;
    parks: ParksConfig;
    water: WaterConfig;
    
}

/**
 * BuildingsConfig
 */
export interface BuildingsConfig {
    chance_no_divide: number;
    max_length: number;
    min_area: number;
    shrink_spacing: number;
    
}

/**
 * RoadConfig
 */
export interface RoadConfig {
    dev_params: RoadDevParams;
    dsep: number;
    dtest: number;
    
}

/**
 * RoadDevParams
 */
export interface RoadDevParams {
    collide_early: number;
    dcircle_join: number;
    dlookahead: number;
    dstep: number;
    join_angle: number;
    path_iterations: number;
    seed_tries: number;
    simplify_tolerance: number;
    
}

/**
 * ParksConfig
 */
export interface ParksConfig {
    cluster_big_parks: boolean;
    num_big_parks: number;
    num_small_parks: number;
    
}

/**
 * WaterConfig
 */
export interface WaterConfig {
    coastline: CoastlineNoise;
    coastline_width: number;
    dev_params: WaterDevParams;
    river: RiverNoise;
    river_bank_size: number;
    river_size: number;
    simplify_tolerance: number;
    
}

/**
 * CoastlineNoise
 */
export interface CoastlineNoise {
    noise_angle: number;
    noise_enabled: boolean;
    noise_size: number;
    
}

/**
 * WaterDevParams
 */
export interface WaterDevParams {
    dcircle_join: number;
    dlookahead: number;
    dsep: number;
    dstep: number;
    dtest: number;
    join_angle: number;
    path_iterations: number;
    seed_tries: number;
    
}

/**
 * RiverNoise
 */
export interface RiverNoise {
    noise_angle: number;
    noise_enabled: boolean;
    noise_size: number;
    
}

/**
 * OptionsConfig
 */
export interface OptionsConfig {
    draw_center: boolean;
    high_dpi: boolean;
    
}

/**
 * Origin
 */
export interface Origin {
    x: number;
    y: number;
    
}

/**
 * ParkPolygonsConfig
 */
export interface ParkPolygonsConfig {
    chance_no_divide: number;
    max_length: number;
    min_area: number;
    shrink_spacing: number;
    
}

/**
 * StyleConfig
 */
export interface StyleConfig {
    building_models: boolean;
    camera_x: number;
    camera_y: number;
    colour_scheme: string;
    orthographic: boolean;
    show_frame: boolean;
    zoom_buildings: boolean;
    
}

/**
 * TensorField
 */
export interface TensorField {
    grids: TensorGrid[];
    radials: TensorRadial[];
    set_recommended: boolean;
    smooth: boolean;
    
}

/**
 * com.example.citybusiness.dto.layout_params.TensorGrid
 *
 * TensorGrid
 */
export interface TensorGrid {
    decay: number;
    size: number;
    theta: number;
    x: number;
    y: number;
    
}

/**
 * com.example.citybusiness.dto.layout_params.TensorRadial
 *
 * TensorRadial
 */
export interface TensorRadial {
    decay: number;
    size: number;
    x: number;
    y: number;
    
}

/**
 * WorldDimensions
 */
export interface WorldDimensions {
    x: number;
    y: number;
    
}