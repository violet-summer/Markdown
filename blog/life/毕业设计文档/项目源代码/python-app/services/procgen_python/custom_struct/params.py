
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class PolygonParams(BaseModel):
    max_length: float
    min_area: float
    shrink_spacing: float
    chance_no_divide: float
    model_config = ConfigDict(extra='forbid')

class GridFieldParams(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    arrays_index: Optional[int] = None
    x: float
    y: float
    size: float
    decay: float
    theta: Optional[float] = None
    model_config = ConfigDict(extra='forbid')

class RadialFieldParams(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    arrays_index: Optional[int] = None
    x: float
    y: float
    size: float
    decay: float
    model_config = ConfigDict(extra='forbid')

class WaterDevParams(BaseModel):
    dsep: float
    dtest: float
    path_iterations: int
    seed_tries: int
    dstep: float
    dlookahead: float
    dcircle_join: float
    join_angle: float
    model_config = ConfigDict(extra='forbid')


class RiverCoastlineParams(BaseModel):
    noise_enabled: bool
    noise_size: float
    noise_angle: float
    model_config = ConfigDict(extra='forbid')


class MapWaterParams(BaseModel):
    simplify_tolerance: float
    coastline: RiverCoastlineParams
    coastline_width: float
    river: RiverCoastlineParams
    dev_params: WaterDevParams
    river_bank_size: float
    river_size: float
    model_config = ConfigDict(extra='forbid')


class MainMajorMinorDevParams(BaseModel):
    path_iterations: int
    seed_tries: int
    dstep: float
    dlookahead: float
    dcircle_join: float
    join_angle: float
    simplify_tolerance: float
    collide_early: bool
    model_config = ConfigDict(extra='forbid')


class MainMajorMinorParams(BaseModel):
    dsep: float
    dtest: float
    dev_params: MainMajorMinorDevParams
    model_config = ConfigDict(extra='forbid')


class MapParksParams(BaseModel):
    cluster_big_parks: bool
    num_big_parks: int
    num_small_parks: int
    model_config = ConfigDict(extra='forbid')


class MapBuildingsParams(BaseModel):
    max_length: float
    min_area: float
    shrink_spacing: float
    chance_no_divide: float
    model_config = ConfigDict(extra='forbid')


class MapParams(BaseModel):
    animate: bool
    animate_speed: float
    water: MapWaterParams
    main: MainMajorMinorParams
    major: MainMajorMinorParams
    minor: MainMajorMinorParams
    parks: MapParksParams
    buildings: MapBuildingsParams
    model_config = ConfigDict(extra='forbid')


class StyleParams(BaseModel):
    colour_scheme: str
    zoom_buildings: bool
    building_models: bool
    show_frame: bool
    orthographic: bool
    camera_x: float
    camera_y: float
    model_config = ConfigDict(extra='forbid')


class OptionsParams(BaseModel):
    draw_center: bool
    high_dpi: bool


class DownloadParams(BaseModel):
    image_scale: float
    type: Optional[str]
    model_config = ConfigDict(extra='forbid')


class TensorFieldParams(BaseModel):
    smooth: bool
    grids: List[GridFieldParams]
    radials: List[RadialFieldParams]
    set_recommended: bool
    model_config = ConfigDict(extra='forbid')

# 这里设置为世界尺度对应的 x 和 z 坐标，但是其它模型格式可能尺度对应关系可能需要变动，因为不同模型约定的xyz轴不一样。
class WorldParams(BaseModel):
    x: float
    y: float
    model_config = ConfigDict(extra='forbid')

class Origin(BaseModel):
    x: float
    y: float
    model_config = ConfigDict(extra='forbid')

import threading
import json
from typing import Optional

# 全局实例缓存和线程锁
_instance_cache: Optional['ALLParams'] = None
_instance_lock = threading.Lock()


class ALLParams(BaseModel):
    world_dimensions: WorldParams
    origin: Origin
    zoom: float
    tensor_field: TensorFieldParams
    map: MapParams
    style: StyleParams
    options: OptionsParams
    download: DownloadParams
    park_polygons: PolygonParams
    model_config = ConfigDict(extra='forbid')

    @staticmethod
    def from_file(file_path: str) -> 'ALLParams':
        """从文件中读取数据并构建 ALLParams 实例"""
        with open(file_path, 'r') as file:
            data = json.load(file)
        return ALLParams(**data)
# 如果存在就直接返回，否则创建一个新的实例
def get_all_params_instance(file_path: str) -> ALLParams:
    """获取 ALLParams 的全局唯一实例（线程安全）"""
    global _instance_cache
    if _instance_cache is None:
        with _instance_lock:
            if _instance_cache is None:  # 双重检查
                _instance_cache = ALLParams.from_file(file_path)
    return _instance_cache