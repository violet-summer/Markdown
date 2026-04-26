/**
 * LayoutJson
 */




/**
 * com.example.citybusiness.dto.LayoutJson.MainExteriorInteriorRoadPolygon
 *
 * MainExteriorInteriorRoadPolygon
 */




/**
 * com.example.citybusiness.dto.LayoutJson.WaterSecondaryRoadPolygon
 *
 * WaterSecondaryRoadPolygon
 */
export interface WaterSecondaryRoadPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * WorldDimensions
 */
export interface WorldDimensions {
    x?: number;
    y?: number;
    [property: string]: any;
}


/**
 * ResponseEntityApiResponseLayoutJson
 */
export interface LayoutJSONResponse {
    code?: number;
    data?: LayoutJson;
    message?: string;
    [property: string]: any;
}


export interface LayoutJson {
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


/**
 * com.example.citybusiness.dto.LayoutJson.BigParksPolygon
 *
 * BigParksPolygon
 */
export interface BigParksPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.BlocksPolygon
 *
 * BlocksPolygon
 */
export interface BlocksPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.CoastlinePolygon
 *
 * CoastlinePolygon
 */
export interface CoastlinePolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.DividedBuildingsPolygons
 *
 * DividedBuildingsPolygons
 */
export interface DividedBuildingsPolygons {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.GroundPolygon
 *
 * GroundPolygon
 */
export interface GroundPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MainExteriorInteriorRoadPolygon
 *
 * MainExteriorInteriorRoadPolygon
 */
export interface MainExteriorInteriorRoadPolygon {
    exterior?: Exterior[];
    interior?: Interior[];
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.Exterior
 *
 * Exterior
 */
export interface Exterior {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.Interior
 *
 * Interior
 */
export interface Interior {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MainNormalRoadPolygon
 *
 * MainNormalRoadPolygon
 */
export interface MainNormalRoadPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MajorExteriorInteriorRoadPolygon
 *
 * MajorExteriorInteriorRoadPolygon
 */
export interface MajorExteriorInteriorRoadPolygon {
    exterior?: Exterior[];
    interior?: Interior[];
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MajorNormalRoadPolygon
 *
 * MajorNormalRoadPolygon
 */
export interface MajorNormalRoadPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MinorExteriorInteriorRoadPolygon
 *
 * MinorExteriorInteriorRoadPolygon
 */
export interface MinorExteriorInteriorRoadPolygon {
    exterior?: Exterior[];
    interior?: Interior[];
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.MinorNormalRoadPolygon
 *
 * MinorNormalRoadPolygon
 */
export interface MinorNormalRoadPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * Origin
 */
export interface Origin {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.PolygonsToProcess
 *
 * PolygonsToProcess
 */
export interface PolygonsToProcess {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.WiverPolygon
 *
 * WiverPolygon
 */
export interface WiverPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.SeaPolygon
 *
 * SeaPolygon
 */
export interface SeaPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.WaterRoadPolygon
 *
 * WaterRoadPolygon
 */
export interface WaterRoadPolygon {
    x?: number;
    y?: number;
    [property: string]: any;
}

/**
 * com.example.citybusiness.dto.LayoutJson.WaterSecondaryRoadPolygon
 *
 * WaterSecondaryRoadPolygon
 */
