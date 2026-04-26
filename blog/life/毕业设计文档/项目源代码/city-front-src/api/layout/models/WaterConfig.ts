/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CoastlineNoise } from './CoastlineNoise';
import type { RiverNoise } from './RiverNoise';
import type { WaterDevParams } from './WaterDevParams';
export type WaterConfig = {
    river_bank_size?: number;
    river_size?: number;
    coastline_width?: number;
    simplify_tolerance?: number;
    dev_params?: WaterDevParams;
    coastline?: CoastlineNoise;
    river?: RiverNoise;
};

