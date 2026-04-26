from pydantic import BaseModel, ConfigDict
from typing import Literal, Optional


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorldDimensions(StrictBaseModel):
    x: int = 640
    y: int = 360


class Origin(StrictBaseModel):
    x: int = 0
    y: int = 0


class TensorGrid(StrictBaseModel):
    x: int
    y: int
    size: int
    decay: int
    theta: int


class TensorRadial(StrictBaseModel):
    x: int
    y: int
    size: int
    decay: int


class TensorField(StrictBaseModel):
    smooth: bool = True
    set_recommended: bool = True
    grids: list[TensorGrid]
    radials: list[TensorRadial]


class CoastlineNoise(StrictBaseModel):
    noise_enabled: bool = True
    noise_size: float = 2
    noise_angle: int = 20


class RiverNoise(StrictBaseModel):
    noise_enabled: bool = True
    noise_size: float = 4
    noise_angle: int = 10


class WaterDevParams(StrictBaseModel):
    dsep: float = 1
    dtest: float = 1
    path_iterations: int = 400
    seed_tries: int = 300
    dstep: float = 1
    dlookahead: float = 100
    dcircle_join: float = 1
    join_angle: float = 0.1


class WaterConfig(StrictBaseModel):
    river_bank_size: float = 10
    river_size: float = 30
    coastline_width:float=5
    coastline: CoastlineNoise
    river: RiverNoise
    simplify_tolerance: float = 0.5
    dev_params: WaterDevParams


class RoadDevParams(StrictBaseModel):
    path_iterations: int = 400
    seed_tries: int = 100
    dstep: float = 1
    dlookahead: float = 300
    dcircle_join: float = 1
    join_angle: float = 0.1
    simplify_tolerance: float = 0.5
    collide_early: int = 0


class RoadConfig(StrictBaseModel):
    dsep: float
    dtest: float
    dev_params: RoadDevParams


class ParksConfig(StrictBaseModel):
    cluster_big_parks: bool = False
    num_big_parks: int = 9
    num_small_parks: int = 10


class BuildingsConfig(StrictBaseModel):
    min_area: float = 10
    max_length: int = 50
    shrink_spacing: int = 2
    chance_no_divide: float = 0.05


class MapConfig(StrictBaseModel):
    animate: bool = True
    animate_speed: int = 10
    water: WaterConfig
    main: RoadConfig
    major: RoadConfig
    minor: RoadConfig
    parks: ParksConfig
    buildings: BuildingsConfig


class StyleConfig(StrictBaseModel):
    colour_scheme: str = "Default"
    zoom_buildings: bool = True
    building_models: bool = True
    show_frame: bool = True
    orthographic: bool = True
    camera_x: int = 0
    camera_y: int = 0


class OptionsConfig(StrictBaseModel):
    draw_center: bool = True
    high_dpi: bool = True


class DownloadConfig(StrictBaseModel):
    image_scale: int = 1
    type: str = ""


class ParkPolygonsConfig(StrictBaseModel):
    max_length: float = 40
    min_area: int = 1
    shrink_spacing: float = 3
    chance_no_divide: int = 0


class LayoutParams(StrictBaseModel):
    world_dimensions: WorldDimensions
    origin: Origin
    zoom: float = 0.1
    tensor_field: TensorField
    map: MapConfig
    style: StyleConfig
    options: OptionsConfig
    download: DownloadConfig
    park_polygons: ParkPolygonsConfig


DEFAULT_LAYOUT_PARAMS = LayoutParams(
    world_dimensions=WorldDimensions(),
    origin=Origin(),
    tensor_field=TensorField(
        grids=[
            TensorGrid(x=40, y=20, size=64, decay=10, theta=59),
            TensorGrid(x=196, y=308, size=48, decay=10, theta=89),
            TensorGrid(x=296, y=60, size=48, decay=10, theta=28),
        ],
        radials=[TensorRadial(x=200, y=200, size=55, decay=5)],
    ),
    map=MapConfig(
        water=WaterConfig(
            coastline=CoastlineNoise(),
            river=RiverNoise(),
            dev_params=WaterDevParams(),
        ),
        main=RoadConfig(
            dsep=40,
            dtest=20,
            dev_params=RoadDevParams(dcircle_join=5),
        ),
        major=RoadConfig(
            dsep=20,
            dtest=100,
            dev_params=RoadDevParams(dcircle_join=3),
        ),
        minor=RoadConfig(
            dsep=4,
            dtest=4,
            dev_params=RoadDevParams(dcircle_join=1),
        ),
        parks=ParksConfig(),
        buildings=BuildingsConfig(),
    ),
    style=StyleConfig(),
    options=OptionsConfig(),
    download=DownloadConfig(),
    park_polygons=ParkPolygonsConfig(),
).model_dump()


class LayoutGenerateRequest(StrictBaseModel):
    params: LayoutParams
    responseMode: Literal["url", "inline"] = "url"
    forceRegenerate: bool = False


class LayoutArtifactsUpdateRequest(StrictBaseModel):
    streamlines: Optional[dict] = None
    polygons: Optional[dict] = None


class LayoutLayerEditRequest(StrictBaseModel):
    """图层编辑请求 - 保存图层可见性等编辑"""
    layoutId: int
    layerVisibility: dict[str, bool]  # {layer_id: visible}
    responseMode: Literal["url", "inline"] = "url"


class LayoutSaveRequest(StrictBaseModel):
    layoutId: int
    svgContent: str
    responseMode: Literal["url", "inline"] = "url"
