---
title: 个人开发web平台基本功能需求
published: 2025-05-26
description: 进行2d轮廓到3d图形转的web页面实现，并且具备svg编辑，自动风格化布局生成的算法
tags:
  - algorithm
  - 3d
  - react
  - web
category: 3d
draft: true
image: /violet.png
---
# 基本技术栈

这里只涉及前端部分，服务端算法在此不讨论，但是会提供相关的接口结构。

1. react
2. web
3. strict ts
4. shadcn
5. r3f
6. obj\svg

# 基本需求

## svg editor

1. 路径绘制并且可选自动闭合
2. 矩形拖拽
3. 点拖动
4. 坐标鼠标悬浮显示
5. 坐标系网格
6. 框选、单选颜色提示
7. 拖动删除等基本功能
8. 导入、导出
9. 层级关系构建，因为每一个轮廓包含关系树都是一个独立模型
10. 不同轮廓高度赋值
11. 层级关系构建交互友好，比如拖动右侧层级树list的item调整父子关系或者兄弟关系
12. 基本元素只有路径和矩形，圆形、曲线使用多点自动逼近。

开放数据到其它组件，没有服务端接口响应的的时候，导出文件到web默认目录下，每次导出自动覆盖。

## 接口结构

### 轮廓层次结构请求


```python
class Point(BaseModel):

    x: float

    y: float

  

class ContourIn(BaseModel):

    path: List[Point]

    height: float

    children: List['ContourIn'] = []

  

ContourIn.model_rebuild()

  

class PathGroupsIn(BaseModel):

    contours: List[ContourIn]
```

### 轮廓层次响应

```python

class ModelInfo(BaseModel):

    model_id: int

    model_data: str

    model_config = ConfigDict(extra='forbid')

  

class ModelResponse(BaseModel):

    models: list[ModelInfo]

    model_config = ConfigDict(extra='forbid')
```

## 3d_scene_lod

这部分内容负责lod加载设置，考虑到模型太多会导致渲染效率低下，我们考虑使用不同距离阈值加载不同的模型

这里的模型是父子关系树替代的，比如两个小立方体，在距离较远的时候自动替换为为一个大的它们两个的合并后的模型，并且一整颗树上的模型都是现成的，只需要不停得加载合适得模型即可

延迟加载：在快速拖动得时候，停止lod加载，在速度较低时重新恢复计算，避免不必要得计算压力

音乐可视化：场景模型会随着音乐音高进行波浪式得高低/大小变换

可视化屏幕：场景中陈列一个屏幕，用于视频播放，图表展示等内容

信息绑定：模型可以绑定、编辑不同的标签信息，进行鼠标选中模型的时候进行展示，发送回数据库，如果没有则保存在本地json文件中






### 接口

#### 

这个脚本内容较为冗余，可以适当删除

```python
from typing import Optional, List

  

from pydantic import BaseModel

  
  

class PositionRotation(BaseModel):

    x: Optional[float] = None

    y: Optional[float] = None

    z: Optional[float] = None

  
  

class Model3D(BaseModel):

  

    global_coordinates: Optional[PositionRotation] = None

    local_coordinates: Optional[PositionRotation] = None

    rotation: Optional[PositionRotation] = None

    model_url: Optional[str] = None

    material_url: Optional[str] = None

    default_texture_url: Optional[str] = None

    default_shader_url: Optional[str] = None

  
  

class Child(BaseModel):

    id: Optional[str] = None

    name: Optional[str] = None

    description: Optional[str] = None

    type: Optional[str] = None

    lod: Optional[int] = None

    model_3d: Optional[Model3D] = None

    children: Optional[List['Child']] = None

  
  

class Sunlight(BaseModel):

    color: Optional[str] = None

    denity: Optional[int] = None

    direction: Optional[PositionRotation] = None

    position: Optional[PositionRotation] = None

  
  

class DefaultBackground(BaseModel):

    ambient_light: Optional[str] = None

    color: Optional[str] = None

    color_alpha: Optional[int] = None

    shadow: Optional[str] = None

    sunlight: Optional[Sunlight] = None

    weather: Optional[str] = None

  
  

class DefaultCamera(BaseModel):

    depth: Optional[int] = None

    id: Optional[str] = None

    position: Optional[PositionRotation] = None

    pov: Optional[int] = None

    view_direction: Optional[PositionRotation] = None

  
  

class Environment(BaseModel):

    weather: Optional[str] = None

    time_of_day: Optional[str] = None

    light_intensity: Optional[int] = None

  
  

class LodSetting(BaseModel):

    lod: Optional[int] = None

    distance: Optional[int] = None

    name: Optional[str] = None

  
  

class BlockModel(BaseModel):

    id: Optional[str] = None

    default_material_url: Optional[str] = None

    default_model_url: Optional[str] = None

    default_shader_url: Optional[str] = None

    default_texture_url: Optional[str] = None

    rotation: Optional[PositionRotation] = None

    scale: Optional[PositionRotation] = None

  
  

class ModelsDefinition(BaseModel):

    id: Optional[str] = None

    name: Optional[str] = None

    description: Optional[str] = None

    block_models: Optional[List[BlockModel]] = None

  
  

class ModelScene(BaseModel):

    user_id: Optional[str] = None

    scene_id: Optional[str] = None

    scene_name: Optional[str] = None

    scene_description: Optional[str] = None

    scene_type: Optional[str] = None

    lod_numbers: Optional[int] = None

    lod_settings: Optional[List[LodSetting]] = None

    models_definitions: Optional[List[ModelsDefinition]] = None

    children: Optional[List[Child]] = None

    environment: Optional[Environment] = None

    default_background: Optional[DefaultBackground] = None

    default_camera: Optional[List[DefaultCamera]] = None

```

#### 响应

响应为服务端的id和模型数据

模型数据可以为obj、stl等格式

## map-gen

通过一个设置面板进行风格化布局自动生成，并且返回svg/obj模型进行渲染，svg进行编辑。

### 接口

#### 请求

基本的请求，这个结构不可变

```python
  

class MapGenReq(BaseModel):

    map_id:int

    user_id:int

    map_name: str

    params:ALLParams

    model_config = ConfigDict(extra='forbid')

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

    dcirclejoin: float

    joinangle: float

    model_config = ConfigDict(extra='forbid')

  
  

class RiverCoastlineParams(BaseModel):

    noise_enabled: bool

    noise_size: float

    noise_angle: float

    model_config = ConfigDict(extra='forbid')

  
  

class MapWaterParams(BaseModel):

    simplify_tolerance: float

    coastline: RiverCoastlineParams

    river: RiverCoastlineParams

    dev_params: WaterDevParams

    river_bank_size: float

    river_size: float

    coastline_width: float

    model_config = ConfigDict(extra='forbid')

  
  

class MainMajorMinorDevParams(BaseModel):

    path_iterations: int

    seed_tries: int

    dstep: float

    dlookahead: float

    dcirclejoin: float

    joinangle: float

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

    cameraX: float

    cameraY: float

    model_config = ConfigDict(extra='forbid')

  
  

class OptionsParams(BaseModel):

    draw_center: bool

    highDPI: bool

  
  

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

  
  

class ALLParams(BaseModel):

    world_dimensions: List[float]

    origin: List[float]

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
```

#### 响应

响应计划为id以及响应的模型数据列表，暂时未定，考虑使用本地路径进行默认加载


# 系统界面要求

三大功能其实是一体的，map-gen负责自动生成svg底座，然后svg编辑器进行布局调整以及轮廓关系树设置，lod负责设置层级关系进行lod加载

默认值：不同部分涉及大量服务端接口，在没有响应的时候使用web项目本地默认json文件进行加载处理，但是接口预留

接口规范：所有的请求以及请求响应结构，都使用结构体约束，并进行分模块管理

由基本完善的首页、登录、控制面板、用户管理界面，参数设置、导出、导入面板

数据流通要明确，方便后续对接其它页面或者服务

关键数据集中管理，不同模块独立目录划分，层次结构分明。


# 服务端数据

初期只管理id、type等数据，并且暂时不考虑使用数据库