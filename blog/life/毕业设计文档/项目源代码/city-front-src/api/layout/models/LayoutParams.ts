/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DownloadConfig } from './DownloadConfig';
import type { MapConfig } from './MapConfig';
import type { OptionsConfig } from './OptionsConfig';
import type { Origin } from './Origin';
import type { ParkPolygonsConfig } from './ParkPolygonsConfig';
import type { StyleConfig } from './StyleConfig';
import type { TensorField } from './TensorField';
import type { WorldDimensions } from './WorldDimensions';
export type LayoutParams = {
    world_dimensions?: WorldDimensions;
    origin?: Origin;
    zoom?: number;
    tensor_field?: TensorField;
    map?: MapConfig;
    style?: StyleConfig;
    options?: OptionsConfig;
    download?: DownloadConfig;
    park_polygons?: ParkPolygonsConfig;
};

