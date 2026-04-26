/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BigParksPolygon } from './BigParksPolygon';
import type { BlocksPolygon } from './BlocksPolygon';
import type { CoastlinePolygon } from './CoastlinePolygon';
import type { DividedBuildingsPolygons } from './DividedBuildingsPolygons';
import type { GroundPolygon } from './GroundPolygon';
import type { MainExteriorInteriorRoadPolygon } from './MainExteriorInteriorRoadPolygon';
import type { MainNormalRoadPolygon } from './MainNormalRoadPolygon';
import type { MajorExteriorInteriorRoadPolygon } from './MajorExteriorInteriorRoadPolygon';
import type { MajorNormalRoadPolygon } from './MajorNormalRoadPolygon';
import type { MinorExteriorInteriorRoadPolygon } from './MinorExteriorInteriorRoadPolygon';
import type { MinorNormalRoadPolygon } from './MinorNormalRoadPolygon';
import type { Origin1 } from './Origin1';
import type { PolygonsToProcess } from './PolygonsToProcess';
import type { SeaPolygon } from './SeaPolygon';
import type { WaterRoadPolygon } from './WaterRoadPolygon';
import type { WaterSecondaryRoadPolygon } from './WaterSecondaryRoadPolygon';
import type { WiverPolygon } from './WiverPolygon';
import type { WorldDimensions2 } from './WorldDimensions2';
export type LayoutJson = {
    world_dimensions: WorldDimensions2;
    river_polygon: Array<WiverPolygon>;
    ground_polygon: Array<GroundPolygon>;
    sea_polygon: Array<SeaPolygon>;
    coastline_polygon: Array<CoastlinePolygon>;
    water_road_polygon: Array<Array<WaterRoadPolygon>>;
    water_secondary_road_polygon: Array<WaterSecondaryRoadPolygon>;
    main_exterior_interior_road_polygon: Array<MainExteriorInteriorRoadPolygon>;
    main_normal_road_polygon: Array<Array<MainNormalRoadPolygon>>;
    major_exterior_interior_road_polygon: Array<MajorExteriorInteriorRoadPolygon>;
    major_normal_road_polygon: Array<Array<MajorNormalRoadPolygon>>;
    minor_exterior_interior_road_polygon: Array<MinorExteriorInteriorRoadPolygon>;
    minor_normal_road_polygon: Array<Array<MinorNormalRoadPolygon>>;
    secondary_road_polygon: string;
    blocks_polygon: Array<Array<BlocksPolygon>>;
    divided_buildings_polygons: Array<Array<DividedBuildingsPolygons>>;
    big_parks_polygon: Array<Array<BigParksPolygon>>;
    small_parks_polygons: Array<string>;
    polygons_to_process: Array<Array<PolygonsToProcess>>;
    origin: Origin1;
};

