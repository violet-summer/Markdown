/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BuildingsConfig } from './BuildingsConfig';
import type { ParksConfig } from './ParksConfig';
import type { RoadConfig } from './RoadConfig';
import type { WaterConfig } from './WaterConfig';
export type MapConfig = {
    animate_speed?: number;
    animate?: boolean;
    water?: WaterConfig;
    main?: RoadConfig;
    major?: RoadConfig;
    minor?: RoadConfig;
    parks?: ParksConfig;
    buildings?: BuildingsConfig;
};

