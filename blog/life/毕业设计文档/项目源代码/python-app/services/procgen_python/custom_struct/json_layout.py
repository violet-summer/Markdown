import json
import os
from dataclasses import dataclass

import logging
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from app.services.mesh_difference import difference_two_meshes, difference_many_meshes
from app.services.storage.file import FileUtil

import numpy as np
import open3d as o3d
from tqdm import tqdm
import trimesh
from trimesh import Trimesh
from shapely.geometry import Polygon as ShapelyPolygon
trimesh.boolean.BLENDER_PATH = r"C:\APP\Blender Foundation\Blender 4.4\blender.exe"
from app.core.config import settings
from app.services.storage import get_minio_storage
from app.services.procgen_python.custom_struct import Vector
from app.services.procgen_python.service import PolygonUtil
from app.services.procgen_python.service.polygon_util import ExteriorInteriorPolygon


class MaterialType(Enum):
    GROUND = "ground"
    WATER = "water"
    METAL = "metal"
    PLASTIC = "plastic"
    GLASS = "glass"
    WOOD = "wood"
    STONE = "stone"
    CONCRETE = "concrete"
    GRASS = "grass"
    PARK = "park"
    BUILDING = "building"
    BLOCK = "block"
    COASTLINE = "coastline"
    ROAD = "road"
    SEA = "sea"
    RIVER = "river"
    BIG_PARK = "big_park"
    SMALL_PARK = "small_park"
    INDEPENDENT_BLOCK = "independent_block"
    DIVIDED_BUILDING = "divided_building"


class json_layout:
    def __init__(
            self,
            json_path: str,
            origin=None,
            world_dimensions=None,
            json_data=None,
            river_polygon=None,
            ground_polygon=None,
            sea_polygon=None,
            coastline_polygon=None,
            water_road_polygon=None,
            water_secondary_road_polygon=None,
            main_exterior_interior_road_polygon=None,
            main_normal_road_polygon=None,
            major_exterior_interior_road_polygon=None,
            major_normal_road_polygon=None,
            minor_exterior_interior_road_polygon=None,
            minor_normal_road_polygon=None,
            secondary_road_polygon=None,
            blocks_polygon=None,
            divided_buildings_polygons=None,
            big_parks_polygon=None,
            small_parks_polygons=None,
        polygons_to_process=None
        ):
            self.world_dimensions = world_dimensions
            self.origin = origin
            self.json_path = json_path
            self.json_data = json_data
            self.river_polygon = river_polygon
            self.ground_polygon = ground_polygon
            self.sea_polygon = sea_polygon
            self.coastline_polygon = coastline_polygon
            self.water_road_polygon = water_road_polygon
            self.water_secondary_road_polygon = water_secondary_road_polygon
            self.main_exterior_interior_road_polygon = main_exterior_interior_road_polygon
            self.main_normal_road_polygon = main_normal_road_polygon
            self.major_exterior_interior_road_polygon:list[ExteriorInteriorPolygon] = major_exterior_interior_road_polygon
            self.major_normal_road_polygon = major_normal_road_polygon
            self.minor_exterior_interior_road_polygon = minor_exterior_interior_road_polygon
            self.minor_normal_road_polygon = minor_normal_road_polygon
            self.secondary_road_polygon = secondary_road_polygon
            self.blocks_polygon = blocks_polygon
            self.divided_buildings_polygons = divided_buildings_polygons
            self.big_parks_polygon = big_parks_polygon
            self.small_parks_polygons = small_parks_polygons
            self.polygons_to_process=polygons_to_process
            self.file_util = FileUtil()

    # def save_layout_json(self, output_dir):
    #     layout_path = Path(output_dir) / "layout.json"
    #     with open(layout_path, "w", encoding="utf-8") as f:
    #         json.dump(self.json_data, f, ensure_ascii=False, indent=2)
    #     file_util = FileUtil()
    #     minio_relative = self._ensure_assets_prefix(layout_path)
    #     file_util.upload_file(layout_path, minio_relative)
    #     return minio_relative

    # def save_streamlines_json(self, output_dir):
    #     streamlines_path = Path(output_dir) / "streamlines.json"
    #     with open(streamlines_path, "w", encoding="utf-8") as f:
    #         json.dump(getattr(self, "streamlines_data", {}), f, ensure_ascii=False, indent=2)
    #     file_util = FileUtil()
    #     minio_relative = self._ensure_assets_prefix(streamlines_path)
    #     file_util.upload_file(streamlines_path, minio_relative)
    #     return minio_relative



    def _ensure_assets_prefix(self, p):
        p = str(p).replace("\\", "/")
        if not p.startswith("assets/"):
            idx = p.find("assets/")
            if idx >= 0:
                p = p[idx:]
            else:
                p = f"assets/{p.lstrip('/')}"
        return p


    @staticmethod
    def dict_to_vector(d):
        if isinstance(d, dict) and 'x' in d and 'y' in d:
            return Vector(x=d['x'], y=d['y'])
        return d

    def dict_to_exterior_interior_polygon(self,d):
        if isinstance(d, dict) and 'exterior' in d and 'interior' in d:
            return ExteriorInteriorPolygon(
                exterior=[self.list_to_vectors(item) for item in d['exterior']],
                interior=[self.list_to_vectors(item) for item in d['interior']]
            )
        return d

    def list_to_vectors(self, item):
        # 递归处理 Vector 或 ExteriorInteriorPolygon
        if isinstance(item, dict) and 'x' in item and 'y' in item:
            return Vector(x=item['x'], y=item['y'])
        elif isinstance(item, dict) and 'exterior' in item and 'interior' in item:
            return self.dict_to_exterior_interior_polygon(item)
        elif isinstance(item, list):
            return [self.list_to_vectors(i) for i in item]
        else:
            return item
    # def list_to_vectors(self, lst):
    #     if isinstance(lst, list):
    #         return [self.list_to_vectors(item) for item in lst]
    #     elif isinstance(lst, dict) and 'x' in lst and 'y' in lst:
    #         return Vector(x=lst['x'], y=lst['y'])
    #     else:
    #         return lst

    # 其它字段同理，按实际类型转换

    def load_json(self) -> None:
        file_util = FileUtil()
        json_content = file_util.read_obj(self.json_path)
        if not json_content:
            self.json_data = None
            return
        self.json_data = json.loads(json_content)
        # 自动填充属性
        data = self.json_data
        self.origin = self.dict_to_vector(data.get('origin', self.origin))
        self.world_dimensions = self.dict_to_vector(data.get('world_dimensions', self.world_dimensions))
        self.river_polygon =  self.list_to_vectors(data.get('river_polygon', self.river_polygon))
        self.ground_polygon = self.list_to_vectors(data.get('ground_polygon', self.ground_polygon))
        self.sea_polygon =  self.list_to_vectors(data.get('sea_polygon', self.sea_polygon))
        self.coastline_polygon = self.list_to_vectors(data.get('coastline_polygon', self.coastline_polygon))
        self.water_road_polygon = self.list_to_vectors(data.get('water_road_polygon', self.water_road_polygon))
        self.water_secondary_road_polygon = self.list_to_vectors(data.get('water_secondary_road_polygon', self.water_secondary_road_polygon))
        self.main_exterior_interior_road_polygon = self.list_to_vectors(data.get('main_exterior_interior_road_polygon', self.main_exterior_interior_road_polygon))
        self.main_normal_road_polygon = self.list_to_vectors(data.get('main_normal_road_polygon', self.main_normal_road_polygon))
        self.major_exterior_interior_road_polygon = self.list_to_vectors(data.get('major_exterior_interior_road_polygon', self.major_exterior_interior_road_polygon))
        self.major_normal_road_polygon = self.list_to_vectors(data.get('major_normal_road_polygon', self.major_normal_road_polygon))
        self.minor_exterior_interior_road_polygon = self.list_to_vectors(data.get('minor_exterior_interior_road_polygon', self.minor_exterior_interior_road_polygon))
        self.minor_normal_road_polygon = self.list_to_vectors(data.get('minor_normal_road_polygon', self.minor_normal_road_polygon))
        self.secondary_road_polygon = self.list_to_vectors(data.get('secondary_road_polygon', self.secondary_road_polygon))
        self.blocks_polygon = self.list_to_vectors(data.get('blocks_polygon', self.blocks_polygon))
        self.divided_buildings_polygons = self.list_to_vectors(data.get('divided_buildings_polygons', self.divided_buildings_polygons))
        self.big_parks_polygon = self.list_to_vectors(data.get('big_parks_polygon', self.big_parks_polygon))
        self.small_parks_polygons = self.list_to_vectors(data.get('small_parks_polygons', self.small_parks_polygons))
        self.polygons_to_process = self.list_to_vectors(data.get('polygons_to_process', self.polygons_to_process))


    @staticmethod
    def to_serializable(obj):
        if hasattr(obj, '__dict__'):
            return {k: json_layout.to_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, (list, tuple)):
            return [json_layout.to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: json_layout.to_serializable(v) for k, v in obj.items()}
        else:
            return obj

    def save_json(self, out_path: str) -> None:
        # 构造要保存的 dict，字段与构造函数参数一致
        data = {
            'origin': self.origin,
            'world_dimensions': self.world_dimensions,
            'river_polygon': self.river_polygon,
            'ground_polygon': self.ground_polygon,
            'sea_polygon': self.sea_polygon,
            'coastline_polygon': self.coastline_polygon,
            'water_road_polygon': self.water_road_polygon,
            'water_secondary_road_polygon': self.water_secondary_road_polygon,
            'main_exterior_interior_road_polygon': self.main_exterior_interior_road_polygon,
            'main_normal_road_polygon': self.main_normal_road_polygon,
            'major_exterior_interior_road_polygon': self.major_exterior_interior_road_polygon,
            'major_normal_road_polygon': self.major_normal_road_polygon,
            'minor_exterior_interior_road_polygon': self.minor_exterior_interior_road_polygon,
            'minor_normal_road_polygon': self.minor_normal_road_polygon,
            'secondary_road_polygon': self.secondary_road_polygon,
            'blocks_polygon': self.blocks_polygon,
            'divided_buildings_polygons': self.divided_buildings_polygons,
            'big_parks_polygon': self.big_parks_polygon,
            'small_parks_polygons': self.small_parks_polygons,
            'polygons_to_process': self.polygons_to_process

        }
        serializable_data = self.to_serializable(data)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
        self.file_util.upload_file(out_path,out_path)

    def generate_complete_svg(self, svg_output_path) -> None:
        """生成包含所有道路、水体、公园、地块等图层的 SVG 文件，兼容 generate_process.py 生成流程和 json_layout 属性。"""
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom.minidom import parseString
        from pathlib import Path

        # 统一 points 序列化，支持 Vector 和 dict
        def points_str(pts):
            if not pts:
                return ""
            return " ".join(f"{p.x if hasattr(p, 'x') else p['x']},{p.y if hasattr(p, 'y') else p['y']}" for p in pts)

        def poly_points_str(pts):
            if not pts:
                return ""
            return " ".join(f"{pt.x if hasattr(pt, 'x') else pt['x']},{pt.y if hasattr(pt, 'y') else pt['y']}" for pt in pts)

        def annulus_path_str(exterior, interior):
            # exterior/interior: list[Vector] or list[dict]
            ext_str = "M " + " ".join(f"{p.x if hasattr(p, 'x') else p['x']},{p.y if hasattr(p, 'y') else p['y']}" for p in exterior) + " Z"
            int_str = "M " + " ".join(f"{p.x if hasattr(p, 'x') else p['x']},{p.y if hasattr(p, 'y') else p['y']}" for p in interior) + " Z"
            return ext_str + " " + int_str

        # 画布尺寸
        # 假设 origin 和 world_dimensions 都是有 x, y 属性的对象
        origin_x = getattr(self.origin, 'x', 0)
        origin_y = getattr(self.origin, 'y', 0)
        world_width = getattr(self.world_dimensions, 'x', 1000)
        world_height = getattr(self.world_dimensions, 'y', 1000)

        # 动态计算基础线宽
        base_stroke_width = max(world_width, world_height) / 1000  # 可根据实际需求调整分母
        ground_stroke = str(base_stroke_width * 0.5)
        sea_stroke = str(base_stroke_width * 0.5)
        coastline_stroke = str(base_stroke_width * 1.5)
        river_stroke = str(base_stroke_width * 0.5)
        main_road_stroke = str(base_stroke_width * 1)
        major_road_stroke = str(base_stroke_width * 1.5)
        minor_road_stroke = str(base_stroke_width * 1)
        park_big_stroke = str(base_stroke_width * 0.5)
        park_small_stroke = str(base_stroke_width * 0.3)
        block_stroke = str(base_stroke_width * 0.3)

        svg = Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(int(world_width)),
            height=str(int(world_height)),
            viewBox=f"{origin_x} {origin_y} {int(world_width)} {int(world_height)}",
            preserveAspectRatio="xMidYMid meet",
        )

        # Ground layer
        ground = getattr(self, 'ground_polygon', None) or getattr(self, 'ground', None)
        if ground:
            ground_group = SubElement(svg, "g", id="layer-ground")
            ground_group.set("class", "layer-ground")
            SubElement(ground_group, "polygon",
                       points=poly_points_str(ground),
                       fill="#d4d4d4", stroke="#999999").set("stroke-width", ground_stroke)

        # Sea layer
        sea = getattr(self, 'sea_polygon', None) or getattr(self, 'sea', None)
        if sea:
            sea_group = SubElement(svg, "g", id="layer-sea")
            sea_group.set("class", "layer-sea")
            SubElement(sea_group, "polygon",
                       points=poly_points_str(sea),
                       fill="#87ceeb", stroke="#5b9bd5").set("stroke-width", sea_stroke)

        # Coastline layer
        coastline = getattr(self, 'coastline_polygon', None) or getattr(self, 'coastline', None)
        if coastline:
            coastline_group = SubElement(svg, "g", id="layer-coastline")
            coastline_group.set("class", "layer-coastline")
            SubElement(coastline_group, "polyline",
                       points=poly_points_str(coastline),
                       fill="none", stroke="#22c55e").set("stroke-width", coastline_stroke)

        # River layer
        river = getattr(self, 'river_polygon', None) or getattr(self, 'river', None)
        if river:
            river_group = SubElement(svg, "g", id="layer-river")
            river_group.set("class", "layer-river")
            SubElement(river_group, "polygon",
                       points=poly_points_str(river),
                       fill="#2563eb", stroke="#1e40af").set("stroke-width", river_stroke)

        # Main roads
        main_roads_normal = getattr(self, 'main_normal_road_polygon', None)
        if main_roads_normal:
            main_roads_group = SubElement(svg, "g", id="layer-roads-main-normal")
            main_roads_group.set("class", "layer-roads-main")
            for idx, road in enumerate(main_roads_normal):
                if road:
                    SubElement(main_roads_group, "polyline",
                               points=poly_points_str(road),
                               fill="rgb(255,0,0)", stroke="none",
                               id=f"road-main-{idx}").set("stroke-width", main_road_stroke)
        main_roads_exterior_interior=getattr(self, 'main_exterior_interior_road_polygon', None)
        if main_roads_exterior_interior:
            main_roads_exterior_interior_group = SubElement(svg, "g", id="layer-roads-main-exterior-interior")
            main_roads_exterior_interior_group.set("class", "layer-roads-main")
            for idx, road in enumerate(main_roads_exterior_interior):
                if road and hasattr(road, "exterior"):
                    if hasattr(road, "interior") and road.interior:
                        path_str = annulus_path_str(road.exterior, road.interior)
                        SubElement(
                            main_roads_exterior_interior_group, "path",
                            d=path_str,
                            fill="rgb(255,0,0)", stroke="none",
                            id=f"road-main-exterior-interior-{idx}",
                            **{"fill-rule": "evenodd"}
                        ).set("stroke-width", main_road_stroke)

        # Major roads
        major_roads_normal = getattr(self, 'major_normal_road_polygon', None)
        if major_roads_normal:
            major_roads_group = SubElement(svg, "g", id="layer-roads-major-normal")
            major_roads_group.set("class", "layer-roads-major")
            for idx, road in enumerate(major_roads_normal):
                if road:
                    SubElement(major_roads_group, "polyline",
                               points=poly_points_str(road),
                               fill="rgb(0,255,0)", stroke="none",
                               id=f"road-major-{idx}").set("stroke-width", major_road_stroke)



        major_roads_exterior_interior = getattr(self, 'major_exterior_interior_road_polygon', None)
        if major_roads_exterior_interior:
            major_roads_exterior_interior_group = SubElement(svg, "g", id="layer-roads-major-exterior-interior")
            major_roads_exterior_interior_group.set("class", "layer-roads-major")
            for idx, road in enumerate(major_roads_exterior_interior):
                if road and hasattr(road, "exterior"):
                    # 直接渲染环形区域，无需判断 interior
                    path_str = annulus_path_str(road.exterior, road.interior)
                    SubElement(
                        major_roads_exterior_interior_group, "path",
                        d=path_str,
                        fill="rgb(0,255,0)", stroke="none",
                        id=f"road-major-exterior-interior-{idx}",
                        **{"fill-rule": "evenodd"}
                    ).set("stroke-width", major_road_stroke)

        # Minor roads
        minor_roads_normal = getattr(self, 'minor_normal_road_polygon', None)
        if minor_roads_normal:
            minor_roads_group = SubElement(svg, "g", id="layer-roads-minor-normal")
            minor_roads_group.set("class", "layer-roads-minor")
            for idx, road in enumerate(minor_roads_normal):
                if road:
                    SubElement(minor_roads_group, "polyline",
                               points=poly_points_str(road),
                               fill="rgb(0,0,255)", stroke="none",
                               id=f"road-minor-{idx}").set("stroke-width", minor_road_stroke)
        minor_roads_exterior_interior = getattr(self, 'minor_exterior_interior_road_polygon', None)
        if minor_roads_exterior_interior:
            minor_roads_exterior_interior_group = SubElement(svg, "g", id="layer-roads-minor-exterior-interior")
            minor_roads_exterior_interior_group.set("class", "layer-roads-minor")
            for idx, road in enumerate(minor_roads_exterior_interior):
                if road and hasattr(road, "exterior"):
                    if hasattr(road, "interior") and road.interior:
                        path_str = annulus_path_str(road.exterior, road.interior)
                        SubElement(
                            minor_roads_exterior_interior_group, "path",
                            d=path_str,
                            fill="rgb(0,0,255)", stroke="none",
                            id=f"road-minor-exterior-interior-{idx}",
                            **{"fill-rule": "evenodd"}
                        ).set("stroke-width", minor_road_stroke)

        # Big parks
        big_parks = getattr(self, 'big_parks_polygon', None) or getattr(self, 'big_parks', None)
        if big_parks:
            big_parks_group = SubElement(svg, "g", id="layer-parks-big")
            big_parks_group.set("class", "layer-parks-big")
            for idx, park in enumerate(big_parks):
                if park:
                    SubElement(big_parks_group, "polygon",
                               points=poly_points_str(park),
                               fill="#4ade80", stroke="#22c55e",
                               id=f"park-big-{idx}").set("stroke-width", park_big_stroke)

        # Small parks
        small_parks = getattr(self, 'small_parks_polygons', None) or getattr(self, 'small_parks', None)
        if small_parks:
            small_parks_group = SubElement(svg, "g", id="layer-parks-small")
            small_parks_group.set("class", "layer-parks-small")
            for idx, park in enumerate(small_parks):
                if park:
                    SubElement(small_parks_group, "polygon",
                               points=poly_points_str(park),
                               fill="#86efac", stroke="#22c55e",
                               id=f"park-small-{idx}").set("stroke-width", park_small_stroke)

        # Blocks (buildings)
        blocks = getattr(self, 'blocks_polygon', None) or getattr(self, 'blocks', None)
        if blocks:
            blocks_group = SubElement(svg, "g", id="layer-blocks")
            blocks_group.set("class", "layer-blocks")
            for idx, block in enumerate(blocks):
                if block:
                    SubElement(blocks_group, "polygon",
                               points=poly_points_str(block),
                               fill="#000000", stroke="#333333",
                               id=f"block-{idx}").set("stroke-width", block_stroke)
        # divided buildings
        divided_buildings = getattr(self, 'divided_buildings_polygons', None) or getattr(self, 'divided_buildings', None)
        if divided_buildings:
            divided_buildings_group = SubElement(svg, "g", id="layer-divided-buildings")
            divided_buildings_group.set("class", "layer-divided-buildings")
            for idx, building in enumerate(divided_buildings):
                if building:
                    SubElement(divided_buildings_group, "polygon",
                               points=poly_points_str(building),
                               fill="#555555", stroke="#222222",
                               id=f"divided-building-{idx}").set("stroke-width", block_stroke)
        # 导出 SVG 文件
        svg_string = parseString(tostring(svg)).toprettyxml(indent="  ")
        # svg_file_path = Path(getattr(self, 'save_dir', './')).joinpath("layout.svg")
        with open(svg_output_path, "w", encoding="utf-8") as svg_file:
            svg_file.write(svg_string)
        logging.info(f"Complete SVG generated: {svg_output_path}")
@dataclass
class MaterialConfig:
    part_colors: Dict[str, list[int]]
    road_level_colors: Dict[str, list[int]]
    default_color: list[int]

    @classmethod
    def default(cls) -> "MaterialConfig":
        return cls(
            part_colors={
                "ground": [170, 170, 170, 255],
                "sea": [70, 130, 180, 255],
                "river": [40, 100, 220, 255],
                "coastline": [244, 164, 96, 255],
                "blocks": [85, 85, 85, 255],
                "independent_blocks": [85, 85, 85, 255],
                "buildings_divided": [210, 210, 210, 255],
                "big_parks": [65, 170, 85, 255],
                "small_parks": [90, 190, 110, 255],
            },
            road_level_colors={
                "roads": [110, 110, 110, 255],
                "main": [95, 95, 95, 255],
                "major": [120, 120, 120, 255],
                "minor": [140, 140, 140, 255],
                "water_main": [130, 130, 130, 255],
                "water_secondary": [150, 150, 150, 255],
            },
            default_color=[180, 180, 180, 255],
        )

    def color_for(self, part_key: str, level_map: Dict[str, str]) -> np.ndarray:
        road_level = level_map.get(part_key)
        if road_level:
            road_color = self.road_level_colors.get(road_level)
            if road_color:
                return np.array(road_color, dtype=np.uint8)
        color = self.part_colors.get(part_key, self.default_color)
        return np.array(color, dtype=np.uint8)

class layout_to_objs:
    ROAD_LEVEL_KEY_MAP = {
        "roads": "roads",
        "main_roads": "main",
        "major_roads": "major",
        "minor_roads": "minor",
        "water_roads": "water_main",
        "water_roads_secondary": "water_secondary",
    }

    def __init__(self, layout_data: json_layout, save_dir: str, material_config: Optional[MaterialConfig] = None):
        self.blocks_geometry = []
        self.roads_geometry = []

        self.layout_data = layout_data
        self.save_dir = save_dir
        self.material_config = material_config or MaterialConfig.default()

    @staticmethod
    def _model_paths(save_dir: str, suffix: str) -> Dict[str, str]:
        ext = suffix.lstrip('.')
        return {
            "ground": str(Path(save_dir).joinpath(f"ground.{ext}")),
            "river": str(Path(save_dir).joinpath(f"river.{ext}")),
            "coastline": str(Path(save_dir).joinpath(f"coastline.{ext}")),
            "water_roads": str(Path(save_dir).joinpath(f"water_roads.{ext}")),
            "water_roads_secondary": str(Path(save_dir).joinpath(f"water_roads_secondary.{ext}")),
            "roads": str(Path(save_dir).joinpath(f"roads.{ext}")),
            "main_roads": str(Path(save_dir).joinpath(f"main_roads.{ext}")),
            "major_roads": str(Path(save_dir).joinpath(f"major_roads.{ext}")),
            "minor_roads": str(Path(save_dir).joinpath(f"minor_roads.{ext}")),
            "buildings_divided": str(Path(save_dir).joinpath(f"buildings_divided.{ext}")),
            "blocks": str(Path(save_dir).joinpath(f"blocks.{ext}")),
            "big_parks": str(Path(save_dir).joinpath(f"big_parks.{ext}")),
            "small_parks": str(Path(save_dir).joinpath(f"small_parks.{ext}")),
            "independent_blocks": str(Path(save_dir).joinpath(f"blocks.{ext}")),
            "sea": str(Path(save_dir).joinpath(f"sea.{ext}")),
            "city_glb": str(Path(save_dir).joinpath("city.glb")),
        }

    def _part_material_color(self, part_key: str) -> np.ndarray:
        return self.material_config.color_for(part_key, self.ROAD_LEVEL_KEY_MAP)

    def _apply_material(self, mesh, key):
        # 类型-材质-颜色映射表
        MODEL_TYPE_MATERIAL_MAP = {
            "ground": {
                "material": MaterialType.GROUND,
                "color": [0.65, 0.45, 0.25, 1.0],  # 棕色
                "metallic": 0.0,
                "roughness": 0.8
            },
            "sea": {
                "material": MaterialType.SEA,
                "color": [70/255, 130/255, 180/255, 0.8],
                "metallic": 0.0,
                "roughness": 0.2
            },
            "river": {
                "material": MaterialType.RIVER,
                "color": [40/255, 100/255, 220/255, 0.8],
                "metallic": 0.0,
                "roughness": 0.2
            },
            "coastline": {
                "material": MaterialType.COASTLINE,
                "color": [244/255, 164/255, 96/255, 1.0],
                "metallic": 0.0,
                "roughness": 0.7
            },
            "blocks": {
                "material": MaterialType.BLOCK,
                "color": [0.95, 0.85, 0.55, 1.0],  # 浅黄色
                "metallic": 0.2,
                "roughness": 0.7
            },
            "independent_blocks": {
                "material": MaterialType.INDEPENDENT_BLOCK,
                "color": [0.85, 0.65, 0.35, 1.0],  # 浅棕色
                "metallic": 0.0,
                "roughness": 0.8
            },
            "buildings_divided": {
                "material": MaterialType.DIVIDED_BUILDING,
                "color": [0.65, 0.75, 0.95, 1.0],  # 浅蓝色
                "metallic": 0.1,
                "roughness": 0.6
            },
            "big_parks": {
                "material": MaterialType.BIG_PARK,
                "color": [65/255, 170/255, 85/255, 1.0],
                "metallic": 0.1,
                "roughness": 0.7
            },
            "small_parks": {
                "material": MaterialType.SMALL_PARK,
                "color": [90/255, 190/255, 110/255, 1.0],
                "metallic": 0.1,
                "roughness": 0.7
            },
            "road": {
                "material": MaterialType.ROAD,
                "color": [0.35, 0.45, 0.65, 1.0],  # 深灰蓝色
                "metallic": 0.3,
                "roughness": 0.9
            },
            "main_roads": {
                "material": MaterialType.ROAD,
                "color": [0.55, 0.65, 0.85, 1.0],  # 浅灰蓝色
                "metallic": 0.3,
                "roughness": 0.9
            },
            "major_roads": {
                "material": MaterialType.ROAD,
                "color": [0.65, 0.75, 0.95, 1.0],  # 浅蓝色
                "metallic": 0.3,
                "roughness": 0.9
            },
            "minor_roads": {
                "material": MaterialType.ROAD,
                "color": [0.85, 0.75, 0.65, 1.0],  # 浅棕色
                "metallic": 0.3,
                "roughness": 0.9
            },
            "water_roads": {
                "material": MaterialType.WATER,
                "color": [130/255, 130/255, 130/255, 0.8],
                "metallic": 0.0,
                "roughness": 0.2
            },
            "water_roads_secondary": {
                "material": MaterialType.WATER,
                "color": [150/255, 150/255, 150/255, 0.8],
                "metallic": 0.0,
                "roughness": 0.2
            },
            "city_glb": {
                "material": MaterialType.BUILDING,
                "color": [0.75, 0.85, 0.95, 1.0],  # 浅灰蓝色
                "metallic": 0.0,
                "roughness": 0.5
            },
        }
        mat = MODEL_TYPE_MATERIAL_MAP.get(key, {
            "material": MaterialType.PLASTIC,
            "color": [0.95, 0.95, 0.95, 1.0],
            "metallic": 0.05,
            "roughness": 0.7
        })
        color = mat["color"]
        # 基于 mesh 唯一标识生成扰动
        mesh_id = getattr(mesh, 'metadata', None)
        if mesh_id is None:
            mesh_id = id(mesh)
        else:
            mesh_id = hash(str(mesh.metadata))
        # 生成扰动（幅度很小，避免破坏整体风格）
        import math
        perturb = (math.sin(mesh_id) * 0.03)  # -0.03~0.03
        # 柔和色系调整
        color = [min(max(c + perturb, 0), 1) for c in color[:3]] + [color[3]]
        metallic = min(max(mat["metallic"] + perturb, 0), 1)
        roughness = min(max(mat["roughness"] + perturb, 0), 1)
        # 设置vertex color
        if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'vertex_colors'):
            mesh.visual.vertex_colors = [color] * len(mesh.vertices)
        else:
            import trimesh
            mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=[color] * len(mesh.vertices))
        # 注入PBR材质（baseColorFactor）
        try:
            from trimesh.visual.material import PBRMaterial
            rgb = color[:3]
            alpha = color[3] if len(color) > 3 else 1.0
            pbr = PBRMaterial(baseColorFactor=rgb + [alpha], metallicFactor=metallic, roughnessFactor=roughness)
            mesh.visual.material = pbr
        except Exception:
            # 兼容trimesh旧版本，降级为SimpleMaterial
            try:
                from trimesh.visual.material import SimpleMaterial
                rgb = color[:3]
                simple = SimpleMaterial(color=rgb)
                mesh.visual.material = simple
            except Exception:
                pass
        # 注入metadata
        if hasattr(mesh, 'metadata'):
            mesh.metadata = mesh.metadata or {}
            mesh.metadata["metallic"] = metallic
            mesh.metadata["roughness"] = roughness
            mesh.metadata["materialType"] = mat["material"].value

    def generate_glb(self) -> Dict[str, str]:
        """Generate part GLBs with materials via trimesh extrusion, independent from OBJ generation API."""
        os.makedirs(self.save_dir, exist_ok=True)
        glb_paths = self._model_paths(self.save_dir, "glb")
        obj_paths = self._model_paths(self.save_dir, "obj")

        layout_snapshot = {
            "ground_polygon": self.layout_data.ground_polygon,
            "river_polygon": self.layout_data.river_polygon,
            "sea_polygon": self.layout_data.sea_polygon,
            "coastline_polygon": self.layout_data.coastline_polygon,
            "water_road_polygon": list(self.layout_data.water_road_polygon or []),
            "water_secondary_road_polygon": self.layout_data.water_secondary_road_polygon,
            "main_exterior_interior_road_polygon": list(self.layout_data.main_exterior_interior_road_polygon or []),
            "main_normal_road_polygon": list(self.layout_data.main_normal_road_polygon or []),
            "major_exterior_interior_road_polygon": list(self.layout_data.major_exterior_interior_road_polygon or []),
            "major_normal_road_polygon": list(self.layout_data.major_normal_road_polygon or []),
            "minor_exterior_interior_road_polygon": list(self.layout_data.minor_exterior_interior_road_polygon or []),
            "minor_normal_road_polygon": list(self.layout_data.minor_normal_road_polygon or []),
            "blocks_polygon": list(self.layout_data.blocks_polygon or []),
            "divided_buildings_polygons": list(self.layout_data.divided_buildings_polygons or []),
            "big_parks_polygon": list(self.layout_data.big_parks_polygon or []),
            "small_parks_polygons": list(self.layout_data.small_parks_polygons or []),
        }

        part_meshes = self._build_part_meshes_from_polygons(layout_snapshot)
        export_keys = [
            "ground", "river", "sea", "coastline", "water_roads", "water_roads_secondary",
            "roads", "main_roads", "major_roads", "minor_roads", "buildings_divided", "blocks",
            "big_parks", "small_parks", "independent_blocks"
        ]

        scene = trimesh.Scene()
        for key in export_keys:
            source_key = "blocks" if key == "independent_blocks" else key
            mesh = part_meshes.get(source_key)
            if mesh is None:
                mesh = self._load_obj_as_trimesh(Path(obj_paths[source_key]))
            if mesh is None:
                continue
            # 导出mesh为glb
            mesh = mesh.copy()
            self._apply_material(mesh, key)
            out_path = Path(glb_paths[key])
            self._export_mesh_to_glb(mesh, out_path)
            scene.add_geometry(mesh, node_name=key, geom_name=key)

        city_glb_path = Path(glb_paths["city_glb"])
        if scene.geometry:
            try:
                scene.export(str(city_glb_path), file_type="glb")
            except Exception as exc:
                logging.exception("Failed to export city.glb")
                glb_paths["city_glb_status"] = "failed"
                glb_paths["city_glb_error"] = str(exc)
        else:
            logging.warning("No geometry available for city.glb in generate_glb")
            glb_paths["city_glb_status"] = "skipped"
            glb_paths["city_glb_error"] = "No geometry available"

        return self._upload_glb_artifacts(glb_paths)

    @staticmethod
    def _load_obj_as_trimesh(obj_path: Path) -> Optional[Trimesh]:
        """Load an OBJ file and normalize it as a single Trimesh instance."""
        if not obj_path.exists():
            return None

        loaded = trimesh.load(str(obj_path), force='mesh', process=False)
        if isinstance(loaded, Trimesh):
            mesh = loaded
        elif isinstance(loaded, trimesh.Scene):
            if not loaded.geometry:
                return None
            mesh = loaded.dump(concatenate=True)
        else:
            return None

        if mesh.faces is None or len(mesh.faces) == 0:
            return None

        # Keep geometry stable while ensuring normals exist for web viewers.
        mesh.remove_unreferenced_vertices()
        mesh.fix_normals()
        return mesh

    @staticmethod
    def _export_mesh_to_glb(mesh: Trimesh, out_path: Path) -> bool:
        """Export one mesh as GLB using trimesh scene pipeline."""
        try:
            scene = trimesh.Scene()
            scene.add_geometry(mesh)
            scene.export(str(out_path), file_type="glb")
            return True
        except Exception:
            logging.exception("Failed to export GLB: %s", out_path)
            return False

    @staticmethod
    def _vector_points_to_xy(polygon) -> list[list[float]]:
        if not polygon:
            return []
        points = []
        for p in polygon:
            if hasattr(p, "x") and hasattr(p, "y"):
                points.append([float(p.x), float(p.y)])
        return points

    @staticmethod
    def _to_ring_list(interior) -> list[list]:
        if not interior:
            return []
        # interior may be one ring[list[Vector]] or many rings[list[list[Vector]]]
        if isinstance(interior, list) and interior and hasattr(interior[0], "x"):
            return [interior]
        return [ring for ring in interior if ring]

    def _polygon_to_extruded_trimesh(self, polygon, top: float, bottom: float) -> Optional[Trimesh]:
        points = self._vector_points_to_xy(polygon)
        # 防御性检查
        if not isinstance(points, (list, tuple, np.ndarray)) or len(points) < 3:
            logging.error(f"_polygon_to_extruded_trimesh: invalid points from polygon, got {type(points)}")
            return None
        if top <= bottom:
            return None
        try:
            # 创建多边形并修复有效性
            base_polygon = ShapelyPolygon(points)
            if not base_polygon.is_valid:
                # 尝试修复：buffer(0) 可以修复自交等问题
                base_polygon = base_polygon.buffer(0)
                if base_polygon.geom_type == 'MultiPolygon':
                    # 如果变成多个多边形，取面积最大的一个（或按需处理）
                    base_polygon = max(base_polygon.geoms, key=lambda p: p.area)
            # 确保外环逆时针（Shapely 构造可能自动处理，但显式确保）
            if not base_polygon.exterior.is_ccw:
                # 反转外壳坐标
                shell = list(base_polygon.exterior.coords)[::-1]
                holes = [list(inner.coords)[::-1] for inner in base_polygon.interiors]  # 内环也反转保持相对方向
                base_polygon = ShapelyPolygon(shell=shell, holes=holes)

            mesh = trimesh.creation.extrude_polygon(base_polygon, height=top - bottom)
            mesh.apply_translation([0.0, 0.0, bottom])
            # 交换 Y 和 Z 轴
            mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
            # 清理与修复
            mesh.merge_vertices()
            mesh.remove_degenerate_faces()
            trimesh.repair.fix_normals(mesh)
            # 检查体积符号
            if mesh.volume < 0:
                mesh.invert()
            trimesh.repair.fill_holes(mesh)
            mesh.remove_unreferenced_vertices()
            # 可选：最终验证
            if not mesh.is_volume:
                logging.warning(f"Extruded mesh is not a volume (volume={mesh.volume})")
            return mesh
        except Exception as e:
            logging.exception(f"Failed to extrude polygon to trimesh: {e}")
            return None

    def _exterior_interior_to_extruded_trimesh(self, exterior_interior_polygon, top: float, bottom: float) -> Optional[
        Trimesh]:
        if not exterior_interior_polygon or top <= bottom:
            return None
        exterior = getattr(exterior_interior_polygon, "exterior", None)
        interior = getattr(exterior_interior_polygon, "interior", None)
        shell = self._vector_points_to_xy(exterior)
        if not isinstance(shell, (list, tuple, np.ndarray)) or len(shell) < 3:
            logging.error(f"Invalid shell from exterior: {type(shell)}")
            return None
        holes = []
        for ring in self._to_ring_list(interior):
            ring_xy = self._vector_points_to_xy(ring)
            if isinstance(ring_xy, (list, tuple, np.ndarray)) and len(ring_xy) >= 3:
                holes.append(ring_xy)
        try:
            # 创建多边形
            base_polygon = ShapelyPolygon(shell=shell, holes=holes if holes else None)
            if not base_polygon.is_valid:
                base_polygon = base_polygon.buffer(0)
                if base_polygon.geom_type == 'MultiPolygon':
                    base_polygon = max(base_polygon.geoms, key=lambda p: p.area)
            # 方向标准化（外环逆时针，内环顺时针）
            if not base_polygon.exterior.is_ccw:
                shell = list(base_polygon.exterior.coords)[::-1]
                holes = [list(inner.coords)[::-1] for inner in base_polygon.interiors]
                base_polygon = ShapelyPolygon(shell=shell, holes=holes)
            else:
                # 外环方向正确，但内环应为顺时针；检查并修正
                oriented_holes = []
                for inner in base_polygon.interiors:
                    if inner.is_ccw:  # 内环应为顺时针，即 is_ccw == False
                        oriented_holes.append(list(inner.coords)[::-1])
                    else:
                        oriented_holes.append(list(inner.coords))
                base_polygon = ShapelyPolygon(shell=list(base_polygon.exterior.coords), holes=oriented_holes)

            mesh = trimesh.creation.extrude_polygon(base_polygon, height=top - bottom)
            mesh.apply_translation([0.0, 0.0, bottom])
            mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
            mesh.merge_vertices()
            mesh.remove_degenerate_faces()
            trimesh.repair.fix_normals(mesh)
            if mesh.volume < 0:
                mesh.invert()
            trimesh.repair.fill_holes(mesh)
            mesh.remove_unreferenced_vertices()
            if not mesh.is_volume:
                logging.warning(f"Extruded exterior/interior mesh is not a volume (volume={mesh.volume})")
            return mesh
        except Exception as e:
            logging.exception(f"Failed to extrude exterior/interior polygon to trimesh: {e}")
            return None
    # def _polygon_to_extruded_trimesh(self, polygon, top: float, bottom: float) -> Optional[Trimesh]:
    #     points = self._vector_points_to_xy(polygon)
    #     if len(points) < 3 or top <= bottom:
    #         return None
    #     try:
    #         base_polygon = ShapelyPolygon(points)
    #         mesh = trimesh.creation.extrude_polygon(base_polygon, height=top - bottom)
    #         # Keep same axis convention as existing generators: Y is height.
    #         mesh.apply_translation([0.0, 0.0, bottom])
    #         mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
    #         mesh.remove_unreferenced_vertices()
    #         mesh.fix_normals()
    #         return mesh
    #     except Exception:
    #         logging.exception("Failed to extrude polygon to trimesh")
    #         return None
    #
    # def _exterior_interior_to_extruded_trimesh(self, exterior_interior_polygon, top: float, bottom: float) -> Optional[Trimesh]:
    #     if not exterior_interior_polygon or top <= bottom:
    #         return None
    #     exterior = getattr(exterior_interior_polygon, "exterior", None)
    #     interior = getattr(exterior_interior_polygon, "interior", None)
    #     shell = self._vector_points_to_xy(exterior)
    #     if len(shell) < 3:
    #         return None
    #     holes = []
    #     for ring in self._to_ring_list(interior):
    #         ring_xy = self._vector_points_to_xy(ring)
    #         if len(ring_xy) >= 3:
    #             holes.append(ring_xy)
    #     try:
    #         base_polygon = ShapelyPolygon(shell=shell, holes=holes if holes else None)
    #         mesh = trimesh.creation.extrude_polygon(base_polygon, height=top - bottom)
    #         mesh.apply_translation([0.0, 0.0, bottom])
    #         mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
    #         mesh.remove_unreferenced_vertices()
    #         mesh.fix_normals()
    #         return mesh
    #     except Exception:
    #         logging.exception("Failed to extrude exterior/interior polygon to trimesh")
    #         return None

    # @staticmethod
    # def _merge_trimesh(meshes: list[Trimesh]) -> Optional[Trimesh]:
    #     valid_meshes = [m for m in meshes if m is not None and hasattr(m, "faces") and len(m.faces) > 0]
    #     if not valid_meshes:
    #         return None
    #     if len(valid_meshes) == 1:
    #         return valid_meshes[0]
    #     merged = trimesh.util.concatenate(valid_meshes)
    #     merged.remove_unreferenced_vertices()
    #     merged.fix_normals()
    #     return merged
    @staticmethod
    def _merge_trimesh(meshes: list[Trimesh]) -> Optional[Trimesh]:
        valid_meshes = [m for m in meshes if m is not None and hasattr(m, "faces") and len(m.faces) > 0]
        if not valid_meshes:
            return None
        if len(valid_meshes) == 1:
            return valid_meshes[0]

        # 从第一个网格开始逐个进行布尔并集
        result = valid_meshes[0]
        for mesh in valid_meshes[1:]:
            try:
                # 使用 blender 引擎（稳定，需要安装 Blender）
                result = result.union(mesh, engine='blender', check_volume=False)
            except Exception as e:
                # 如果 blender 失败，尝试回退到 manifold
                try:
                    result = result.union(mesh, engine='manifold', check_volume=False)
                except Exception as e2:
                    logging.error(f"布尔并集失败: {e2}")
                    return None
            if result is None or result.is_empty:
                return None

        # 后处理
        result.remove_unreferenced_vertices()
        result.remove_degenerate_faces()
        trimesh.repair.fix_normals(result)
        if result.volume < 0:
            result.invert()
        return result

    def _build_part_meshes_from_polygons(self, layout_snapshot: Dict[str, object]) -> Dict[str, Trimesh]:
        import shapely.geometry as sg
        from shapely.ops import unary_union
        import trimesh
        import numpy as np
        from typing import Optional, List, Union

        part_meshes: Dict[str, Trimesh] = {}

        # -------------------- 辅助函数：将原始多边形转换为 Shapely 对象 --------------------
        def to_shapely_polygon(obj) -> Optional[sg.Polygon]:
            """将原始多边形对象转换为 Shapely Polygon"""
            points = self._vector_points_to_xy(obj)
            if not isinstance(points, (list, tuple, np.ndarray)) or len(points) < 3:
                return None
            poly = sg.Polygon(points)
            if not poly.is_valid:
                poly = poly.buffer(0)
                if poly.geom_type == 'MultiPolygon':
                    # 取面积最大的部分，可根据需要调整
                    poly = max(poly.geoms, key=lambda p: p.area)
            return poly

        def to_shapely_multi(poly_list) -> Optional[sg.MultiPolygon]:
            """将原始多边形列表转换为 Shapely MultiPolygon（过滤无效）"""
            polys = []
            for p in poly_list:
                sp = to_shapely_polygon(p)
                if sp is not None and not sp.is_empty:
                    polys.append(sp)
            if not polys:
                return None
            return sg.MultiPolygon(polys)

        # -------------------- 辅助函数：从原始带孔多边形转换为 Shapely Polygon（带孔） --------------------
        def to_shapely_with_holes(obj) -> Optional[sg.Polygon]:
            """处理 exterior/interior 结构的原始多边形，返回 Shapely Polygon（可能带孔）"""
            if not obj:
                return None
            exterior = getattr(obj, "exterior", None)
            interior = getattr(obj, "interior", None)
            shell_pts = self._vector_points_to_xy(exterior)
            if not isinstance(shell_pts, (list, tuple, np.ndarray)) or len(shell_pts) < 3:
                return None
            holes_pts = []
            for ring in self._to_ring_list(interior):
                ring_xy = self._vector_points_to_xy(ring)
                if isinstance(ring_xy, (list, tuple, np.ndarray)) and len(ring_xy) >= 3:
                    holes_pts.append(ring_xy)
            poly = sg.Polygon(shell=shell_pts, holes=holes_pts if holes_pts else None)
            if not poly.is_valid:
                poly = poly.buffer(0)
                if poly.geom_type == 'MultiPolygon':
                    poly = max(poly.geoms, key=lambda p: p.area)
            return poly

        # -------------------- 辅助函数：将 Shapely 对象挤出为 Trimesh --------------------
        def _extrude_shapely(shapely_obj, top: float, bottom: float, name: str = "") -> Optional[Trimesh]:
            """将 Shapely Polygon 或 MultiPolygon 挤出为 Trimesh，并平移到正确高度"""
            if shapely_obj is None or shapely_obj.is_empty:
                return None
            height = top - bottom
            meshes = []

            # 统一处理为可迭代的 Polygon 列表
            if shapely_obj.geom_type == 'Polygon':
                polys = [shapely_obj]
            elif shapely_obj.geom_type == 'MultiPolygon':
                polys = list(shapely_obj.geoms)
            else:
                logging.warning(f"Unsupported geometry type: {shapely_obj.geom_type}")
                return None

            for poly in polys:
                try:
                    mesh = trimesh.creation.extrude_polygon(poly, height=height)
                    # 平移到底部高度
                    mesh.apply_translation([0.0, 0.0, bottom])
                    # 交换 Y 和 Z 轴
                    mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
                    # 清理与修复（复用你原有的清理步骤）
                    mesh.merge_vertices()
                    mesh.remove_degenerate_faces()
                    trimesh.repair.fix_normals(mesh)
                    if mesh.volume < 0:
                        mesh.invert()
                    trimesh.repair.fill_holes(mesh)
                    mesh.remove_unreferenced_vertices()
                    if not mesh.is_volume:
                        logging.warning(f"Extruded mesh '{name}' is not a volume (volume={mesh.volume})")
                    meshes.append(mesh)
                except Exception as e:
                    logging.exception(f"Failed to extrude polygon '{name}': {e}")
                    continue

            if not meshes:
                return None
            if len(meshes) == 1:
                return meshes[0]
            # 合并多个网格（它们空间上不重叠，简单拼接即可）
            merged = trimesh.util.concatenate(meshes)
            merged.remove_unreferenced_vertices()
            return merged

        # -------------------- 1. 将原始多边形转换为 Shapely 对象 --------------------
        # 地面、河流、海域、海岸线（假设它们是简单多边形）
        ground_poly = to_shapely_polygon(layout_snapshot.get("ground_polygon"))
        river_poly = to_shapely_polygon(layout_snapshot.get("river_polygon"))
        sea_poly = to_shapely_polygon(layout_snapshot.get("sea_polygon"))
        coast_poly = to_shapely_polygon(layout_snapshot.get("coastline_polygon"))

        # 道路：可能有多个列表，包含简单多边形和带孔多边形
        main_exterior = layout_snapshot.get("main_exterior_interior_road_polygon") or []
        main_normal = layout_snapshot.get("main_normal_road_polygon") or []
        major_exterior = layout_snapshot.get("major_exterior_interior_road_polygon") or []
        major_normal = layout_snapshot.get("major_normal_road_polygon") or []
        minor_exterior = layout_snapshot.get("minor_exterior_interior_road_polygon") or []
        minor_normal = layout_snapshot.get("minor_normal_road_polygon") or []
        water_roads_list = layout_snapshot.get("water_road_polygon") or []
        water_secondary = layout_snapshot.get("water_secondary_road_polygon")  # 单个

        # 将每个道路列表转换为 Shapely 多边形集合
        def convert_road_list(road_objs, use_holes=False):
            polys = []
            for obj in road_objs:
                if obj is None:
                    continue
                if use_holes:
                    p = to_shapely_with_holes(obj)
                else:
                    p = to_shapely_polygon(obj)
                if p is not None and not p.is_empty:
                    polys.append(p)
            return polys

        main_polys = convert_road_list(main_exterior, use_holes=True) + convert_road_list(main_normal)
        major_polys = convert_road_list(major_exterior, use_holes=True) + convert_road_list(major_normal)
        minor_polys = convert_road_list(minor_exterior, use_holes=True) + convert_road_list(minor_normal)
        water_polys = convert_road_list(water_roads_list)
        water_secondary_poly = to_shapely_polygon(water_secondary) if water_secondary else None

        # 公园和建筑等
        big_parks_list = layout_snapshot.get("big_parks_polygon") or []
        small_parks_list = layout_snapshot.get("small_parks_polygons") or []
        blocks_list = layout_snapshot.get("blocks_polygon") or []
        buildings_list = layout_snapshot.get("divided_buildings_polygons") or []

        big_parks_polys = convert_road_list(big_parks_list)  # 简单多边形
        small_parks_polys = convert_road_list(small_parks_list)
        blocks_polys = convert_road_list(blocks_list)
        buildings_polys = convert_road_list(buildings_list)

        # -------------------- 2. 二维布尔运算 --------------------
        # 地面减去河流、海域、海岸线
        ground_poly_origin=ground_poly
        if ground_poly:
            if river_poly:
                ground_poly = ground_poly.difference(river_poly)
            if sea_poly:
                ground_poly = ground_poly.difference(sea_poly)
            if coast_poly:
                ground_poly = ground_poly.difference(coast_poly)

        # 海域减去河流
        if sea_poly and river_poly:
            sea_poly = sea_poly.difference(river_poly)
        if sea_poly and coast_poly:
            sea_poly = sea_poly.difference(coast_poly)

        # 海岸线减去河流
        if coast_poly and river_poly:
            coast_poly = coast_poly.difference(river_poly)

        # 道路合并与层级差集
        def merge_polys(poly_list):
            if not poly_list:
                return None
            if len(poly_list) == 1:
                return poly_list[0]
            return unary_union(poly_list)

        main_union = merge_polys(main_polys)
        major_union = merge_polys(major_polys)
        minor_union = merge_polys(minor_polys)
        water_union = merge_polys(water_polys)

        # 主路 = (主路基础 ∪ 水域主路) - 主要道路 - 次要道路
        if main_union is not None:
            main_roads_poly = main_union
            if water_union is not None:
                main_roads_poly = main_roads_poly.union(water_union)
            if major_union is not None:
                main_roads_poly = main_roads_poly.difference(major_union)
            if minor_union is not None:
                main_roads_poly = main_roads_poly.difference(minor_union)
        else:
            main_roads_poly = None

        # 主要道路 = 主要道路 - 次要道路
        if major_union is not None:
            major_roads_poly = major_union
            if minor_union is not None:
                major_roads_poly = major_roads_poly.difference(minor_union)
        else:
            major_roads_poly = None

        # 次要道路不变
        minor_roads_poly = minor_union

        # 所有道路的并集（用于公园减法）
        all_roads_polys = [p for p in
                           [main_roads_poly, major_roads_poly, minor_roads_poly, water_union, water_secondary_poly] if
                           p is not None]
        all_roads_union = unary_union(all_roads_polys) if all_roads_polys else None

        # 公园减去所有道路
        def subtract_roads_from_parks(parks):
            result = []
            for p in parks:
                if p is None or p.is_empty:
                    continue
                if all_roads_union is not None:
                    p = p.difference(all_roads_union)
                if not p.is_empty:
                    if p.geom_type == 'MultiPolygon':
                        result.extend(list(p.geoms))
                    else:
                        result.append(p)
            return result

        big_parks_polys = subtract_roads_from_parks(big_parks_polys)
        small_parks_polys = subtract_roads_from_parks(small_parks_polys)

        # 区块和建筑物通常无需与其他做差集，直接使用原始多边形（但可能需要合并为单一 MultiPolygon）
        blocks_union = merge_polys(blocks_polys)
        buildings_union = merge_polys(buildings_polys)

        # -------------------- 3. 挤出为三维网格 --------------------
        ground = _extrude_shapely(ground_poly, LevelTopBottomHeight.ground_top, LevelTopBottomHeight.river_bottom,
                                  "ground")
        river = _extrude_shapely(river_poly, LevelTopBottomHeight.river_top, LevelTopBottomHeight.river_bottom, "river")
        sea = _extrude_shapely(sea_poly, LevelTopBottomHeight.sea_top, LevelTopBottomHeight.sea_bottom, "sea")
        coastline = _extrude_shapely(coast_poly, LevelTopBottomHeight.coastline_top,
                                     LevelTopBottomHeight.coastline_bottom, "coastline")
        ground_poly_origin_mesh=_extrude_shapely(ground_poly_origin, LevelTopBottomHeight.river_bottom, LevelTopBottomHeight.ground_bottom,
                                  "ground_poly_origin")
        ground=ground.union(ground_poly_origin_mesh)
        # river_ground = _extrude_shapely(river_poly, LevelTopBottomHeight.river_bottom, LevelTopBottomHeight.ground_bottom, "river")
        # sea_ground = _extrude_shapely(sea_poly, LevelTopBottomHeight.sea_bottom, LevelTopBottomHeight.ground_bottom, "sea")
        # coastline_ground = _extrude_shapely(coast_poly, LevelTopBottomHeight.coastline_bottom,
        #                              LevelTopBottomHeight.ground_bottom, "coastline")
        # ground=ground.union(river_ground) if river_ground else None
        # ground=ground.union(sea_ground) if sea_ground else None
        # ground=ground.union(coastline_ground) if coastline_ground else None

        main_roads = _extrude_shapely(main_roads_poly, LevelTopBottomHeight.main_road_top,
                                      LevelTopBottomHeight.main_road_bottom, "main_roads")
        major_roads = _extrude_shapely(major_roads_poly, LevelTopBottomHeight.major_road_top,
                                       LevelTopBottomHeight.major_road_bottom, "major_roads")
        minor_roads = _extrude_shapely(minor_roads_poly, LevelTopBottomHeight.minor_road_top,
                                       LevelTopBottomHeight.minor_road_bottom, "minor_roads")
        water_roads = _extrude_shapely(water_union, LevelTopBottomHeight.main_road_top,
                                       LevelTopBottomHeight.main_road_bottom, "water_roads")
        water_roads_secondary = _extrude_shapely(water_secondary_poly, LevelTopBottomHeight.main_road_top,
                                                 LevelTopBottomHeight.main_road_bottom, "water_roads_secondary")

        # big_parks = _extrude_shapely(big_parks_polys, LevelTopBottomHeight.big_park_top,
        #                              LevelTopBottomHeight.big_park_bottom, "big_parks") if big_parks_polys else None
        # small_parks = _extrude_shapely(small_parks_polys, LevelTopBottomHeight.small_park_top,
        #                                LevelTopBottomHeight.small_park_bottom,
        #                                "small_parks") if small_parks_polys else None

        # 在公园处理后添加转换函数
        def list_to_geometry(poly_list):
            """将多边形列表转换为 Shapely 几何对象（单个 Polygon 或 MultiPolygon）"""
            if not poly_list:
                return None
            # 过滤无效或空多边形
            valid = [p for p in poly_list if p is not None and not p.is_empty]
            if not valid:
                return None
            if len(valid) == 1:
                return valid[0]
            return sg.MultiPolygon(valid)

        # 公园减去所有道路后得到列表
        big_parks_polys = subtract_roads_from_parks(big_parks_polys)
        small_parks_polys = subtract_roads_from_parks(small_parks_polys)

        # 转换为几何对象
        big_parks_geom = list_to_geometry(big_parks_polys)
        small_parks_geom = list_to_geometry(small_parks_polys)

        # 挤出
        big_parks = _extrude_shapely(big_parks_geom, LevelTopBottomHeight.big_park_top,
                                     LevelTopBottomHeight.big_park_bottom, "big_parks") if big_parks_geom else None
        small_parks = _extrude_shapely(small_parks_geom, LevelTopBottomHeight.small_park_top,
                                       LevelTopBottomHeight.small_park_bottom,
                                       "small_parks") if small_parks_geom else None
        blocks = _extrude_shapely(blocks_union, LevelTopBottomHeight.blocks_top, LevelTopBottomHeight.blocks_bottom,
                                  "blocks")
        buildings = _extrude_shapely(buildings_union, LevelTopBottomHeight.building_top,
                                     LevelTopBottomHeight.building_bottom, "buildings")

        # -------------------- 4. 组装 part_meshes --------------------
        part_meshes["ground"] = ground
        part_meshes["river"] = river
        part_meshes["sea"] = sea
        part_meshes["coastline"] = coastline
        part_meshes["main_roads"] = main_roads
        part_meshes["major_roads"] = major_roads
        part_meshes["minor_roads"] = minor_roads
        part_meshes["water_roads"] = water_roads
        part_meshes["water_roads_secondary"] = water_roads_secondary
        part_meshes["big_parks"] = big_parks
        part_meshes["small_parks"] = small_parks
        part_meshes["blocks"] = blocks
        part_meshes["buildings_divided"] = buildings

        # -------------------- 5. 诊断与导出 --------------------
        self.diagnose_mesh(mesh=ground, name="ground", export_debug=True)
        self.diagnose_mesh(mesh=river, name="river", export_debug=True)
        self.diagnose_mesh(mesh=sea, name="sea", export_debug=True)

        # 合并所有网格导出测试（可选）
        all_meshes = [m for m in [ground, river, sea, coastline, main_roads, major_roads, minor_roads,
                                  water_roads, water_roads_secondary, blocks, buildings,
                                  big_parks, small_parks] if m is not None]
        if all_meshes:
            all_mesh = trimesh.util.concatenate(all_meshes)
            all_mesh.export("D://CODE//3d_city//app//services//test//test.glb", file_type="glb")
            logging.info("生成test-full模型成功")
        else:
            logging.error("没有生成任何有效网格")

        return part_meshes
    # def _build_part_meshes_from_polygons(self, layout_snapshot: Dict[str, object]) -> Dict[str, Trimesh]:
    #     part_meshes: Dict[str, Trimesh] = {}
    #     ground_points=self._vector_points_to_xy(layout_snapshot.get("ground_polygon"))
    #     river_points=self._vector_points_to_xy(layout_snapshot.get("river_polygon"))
    #     sea_points = self._vector_points_to_xy(layout_snapshot.get("sea_polygon"))
    #     coast_points = self._vector_points_to_xy(layout_snapshot.get("coast_polygon"))
    #     ground_shapely=ShapelyPolygon(ground_points)
    #     river_shapely = ShapelyPolygon(river_points)
    #     sea_shapely = ShapelyPolygon(sea_points)
    #     coast_shapely = ShapelyPolygon(coast_points)
    #     ground_shapely=ground_shapely.difference(river_shapely)
    #     ground_shapely=ground_shapely.difference(sea_shapely)
    #     ground_shapely=ground_shapely.difference(coast_shapely)
    #     coast_shapely=coast_shapely.difference(river_shapely)
    #     sea_shapely=sea_shapely.difference(river_shapely)
    #
    #
    #     ground = self._polygon_to_extruded_trimesh(layout_snapshot.get("ground_polygon"), LevelTopBottomHeight.ground_top, LevelTopBottomHeight.ground_bottom)
    #     river = self._polygon_to_extruded_trimesh(layout_snapshot.get("river_polygon"), LevelTopBottomHeight.river_top, LevelTopBottomHeight.river_bottom)
    #     sea = self._polygon_to_extruded_trimesh(layout_snapshot.get("sea_polygon"), LevelTopBottomHeight.sea_top, LevelTopBottomHeight.sea_bottom)
    #     coastline = self._polygon_to_extruded_trimesh(layout_snapshot.get("coastline_polygon"), LevelTopBottomHeight.coastline_top, LevelTopBottomHeight.coastline_bottom)
    #
    #     # coastline = difference_two_meshes(coastline, river)
    #     self.diagnose_mesh(mesh=coastline, name="coastline1", export_debug=True)
    #     self.diagnose_mesh(mesh=sea, name="sea1", export_debug=True)
    #     self.diagnose_mesh(mesh=ground, name="ground1", export_debug=True)
    #     # coastline_temp=coastline.intersection(ground)
    #     # river_temp = river.intersection(ground)
    #     # sea=sea.difference(coastline_temp)
    #     # # sea=sea.difference(river_temp)
    #     # river=river.intersection(ground)
    #     # river=river.difference(sea)
    #     # self.diagnose_mesh(mesh=sea, name="sea2", export_debug=True)
    #     # self.diagnose_mesh(mesh=ground, name="ground1", export_debug=True)
    #     # ground=ground.difference(sea)
    #     # self.diagnose_mesh(mesh=ground, name="ground2", export_debug=True)
    #     # ground=ground.difference()
    #     # sea=sea.intersection(ground)
    #     import trimesh
    #     from shapely.geometry import Polygon, MultiPolygon
    #
    #     def extrude_any_polygon(shapely_obj, height):
    #         meshes = []
    #         if isinstance(shapely_obj, Polygon):
    #             meshes.append(trimesh.creation.extrude_polygon(shapely_obj, height=height))
    #         elif isinstance(shapely_obj, MultiPolygon):
    #             for poly in shapely_obj.geoms:
    #                 meshes.append(trimesh.creation.extrude_polygon(poly, height=height))
    #         else:
    #             raise TypeError("Input must be Polygon or MultiPolygon")
    #
    #         # 交换 Y 和 Z 轴
    #         for mesh in meshes:
    #             mesh.apply_translation([0.0, 0.0, 0])
    #             mesh.vertices[:, [1, 2]] = mesh.vertices[:, [2, 1]]
    #             # 清理与修复
    #             mesh.merge_vertices()
    #             mesh.remove_degenerate_faces()
    #             trimesh.repair.fix_normals(mesh)
    #         return self._merge_trimesh(meshes) if len(meshes) > 1 else meshes[0]
    #
    #     # 用法举例
    #     ground = extrude_any_polygon(ground_shapely,LevelTopBottomHeight.ground_top - LevelTopBottomHeight.ground_bottom)
    #     sea = extrude_any_polygon(sea_shapely, LevelTopBottomHeight.sea_top - LevelTopBottomHeight.sea_bottom)
    #     # coastline = extrude_any_polygon(coast_shapely,
    #     #                                 LevelTopBottomHeight.coastline_top - LevelTopBottomHeight.coastline_bottom)
    #     # river = extrude_any_polygon(river_shapely,height=LevelTopBottomHeight.river_top - LevelTopBottomHeight.river_bottom)
    #
    #     # ground=trimesh.creation.extrude_polygon(ground_shapely, height=LevelTopBottomHeight.ground_top - LevelTopBottomHeight.ground_bottom)
    #     # sea=trimesh.creation.extrude_polygon(sea_shapely,height=LevelTopBottomHeight.sea_top-LevelTopBottomHeight.sea_bottom)
    #     # coastline=trimesh.creation.extrude_polygon(coast_shapely,height=LevelTopBottomHeight.coastline_top-LevelTopBottomHeight.coastline_bottom)
    #     # river=trimesh.creation.extrude_polygon(river_shapely,height=LevelTopBottomHeight.river_top-LevelTopBottomHeight.river_bottom)
    #
    #     # coastline=difference_two_meshes(coastline, river)
    #     self.diagnose_mesh(mesh=river, name="river1", export_debug=True)
    #     river.export(Path("C:\\APP\\CODE\\3d_city\\app\\services\\test\\river_before.glb"), file_type="glb")
    #
    #     # ground=ground.difference( river,engine='blender')
    #     ground.export(Path("C:\\APP\\CODE\\3d_city\\app\\services\\test\\ground_before.glb"),file_type="glb")
    #     self.diagnose_mesh(mesh=ground, name="ground2", export_debug=True)
    #     # ground =ground.difference(sea,engine='blender')
    #     ground.export(Path("C:\\APP\\CODE\\3d_city\\app\\services\\test\\ground_before_3.glb"), file_type="glb")
    #     self.diagnose_mesh(mesh=ground, name="ground3", export_debug=True)
    #     # sea = sea.difference( river,engine='blender')
    #     self.diagnose_mesh(mesh=sea, name="sea2", export_debug=True)
    #     # sea=sea.difference(coastline,engine='blender')
    #
    #     # river = self._polygon_to_extruded_trimesh(layout_snapshot.get("river_polygon"), LevelTopBottomHeight.river_top,
    #     #                                           LevelTopBottomHeight.river_bottom)
    #
    #     # coastline=coastline.intersection(ground)
    #     # ground=difference_many_meshes([ground, sea,river,coastline])
    #     logging.info("开始处理返回数据")
    #     if ground is not None:
    #         part_meshes["ground"] = ground
    #     if river is not None:
    #         part_meshes["river"] = river
    #     if sea is not None:
    #         part_meshes["sea"] = sea
    #     if coastline is not None:
    #         part_meshes["coastline"] = coastline
    #     logging.info("开始处理返回数据-水路")
    #     water_roads = self._merge_trimesh([
    #         self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.main_road_top, LevelTopBottomHeight.main_road_bottom)
    #         for p in (layout_snapshot.get("water_road_polygon") or [])
    #     ])
    #     if water_roads is not None:
    #         part_meshes["water_roads"] = water_roads
    #
    #     water_roads_secondary = self._polygon_to_extruded_trimesh(
    #         layout_snapshot.get("water_secondary_road_polygon"),
    #         LevelTopBottomHeight.main_road_top,
    #         LevelTopBottomHeight.main_road_bottom,
    #     )
    #     if water_roads_secondary is not None:
    #         part_meshes["water_roads_secondary"] = water_roads_secondary
    #     logging.info("开始处理挤出道路")
    #     main_roads_base = self._merge_trimesh(
    #         [
    #             *[
    #                 self._exterior_interior_to_extruded_trimesh(p, LevelTopBottomHeight.main_road_top, LevelTopBottomHeight.main_road_bottom)
    #                 for p in (layout_snapshot.get("main_exterior_interior_road_polygon") or [])
    #             ],
    #             *[
    #                 self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.main_road_top, LevelTopBottomHeight.main_road_bottom)
    #                 for p in (layout_snapshot.get("main_normal_road_polygon") or [])
    #             ],
    #         ]
    #     )
    #     major_roads = self._merge_trimesh(
    #         [
    #             *[
    #                 self._exterior_interior_to_extruded_trimesh(p, LevelTopBottomHeight.major_road_top, LevelTopBottomHeight.major_road_bottom)
    #                 for p in (layout_snapshot.get("major_exterior_interior_road_polygon") or [])
    #             ],
    #             *[
    #                 self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.major_road_top, LevelTopBottomHeight.major_road_bottom)
    #                 for p in (layout_snapshot.get("major_normal_road_polygon") or [])
    #             ],
    #         ]
    #     )
    #     minor_roads_base = self._merge_trimesh(
    #         [
    #             *[
    #                 self._exterior_interior_to_extruded_trimesh(p, LevelTopBottomHeight.minor_road_top, LevelTopBottomHeight.minor_road_bottom)
    #                 for p in (layout_snapshot.get("minor_exterior_interior_road_polygon") or [])
    #             ],
    #             *[
    #                 self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.minor_road_top, LevelTopBottomHeight.minor_road_bottom)
    #                 for p in (layout_snapshot.get("minor_normal_road_polygon") or [])
    #             ],
    #         ]
    #     )
    #     logging.info("开始处理道路")
    #     main_roads = self._merge_trimesh([main_roads_base, water_roads])
    #     minor_roads = self._merge_trimesh([minor_roads_base, water_roads_secondary])
    #     roads = self._merge_trimesh([main_roads_base, major_roads, minor_roads_base])
    #
    #     if main_roads is not None:
    #         main_roads=difference_many_meshes([main_roads,major_roads,minor_roads])
    #         part_meshes["main_roads"] = main_roads
    #     if major_roads is not None:
    #         major_roads=difference_many_meshes([major_roads,minor_roads])
    #         part_meshes["major_roads"] = major_roads
    #     if minor_roads is not None:
    #         part_meshes["minor_roads"] = minor_roads
    #     if roads is not None:
    #         part_meshes["roads"] = roads
    #     logging.info("开始处理blocks")
    #     blocks = self._merge_trimesh([
    #         self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.blocks_top, LevelTopBottomHeight.blocks_bottom)
    #         for p in (layout_snapshot.get("blocks_polygon") or [])
    #     ])
    #     buildings = self._merge_trimesh([
    #         self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.building_top, LevelTopBottomHeight.building_bottom)
    #         for p in (layout_snapshot.get("divided_buildings_polygons") or [])
    #     ])
    #     big_parks = self._merge_trimesh([
    #         self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.big_park_top, LevelTopBottomHeight.big_park_bottom)
    #         for p in (layout_snapshot.get("big_parks_polygon") or [])
    #     ])
    #
    #     small_parks = self._merge_trimesh([
    #         self._polygon_to_extruded_trimesh(p, LevelTopBottomHeight.small_park_top, LevelTopBottomHeight.small_park_bottom)
    #         for p in (layout_snapshot.get("small_parks_polygons") or [])
    #     ])
    #     if blocks is not None:
    #         part_meshes["blocks"] = blocks
    #     if buildings is not None:
    #         part_meshes["buildings_divided"] = buildings
    #     if big_parks is not None:
    #         big_parks=big_parks.difference(major_roads)
    #         big_parks=big_parks.difference(minor_roads)
    #         big_parks=big_parks.difference(main_roads)
    #         part_meshes["big_parks"] = big_parks
    #     if small_parks is not None:
    #         small_parks=difference_many_meshes([small_parks, major_roads, main_roads, minor_roads])
    #         part_meshes["small_parks"] = small_parks
    #
    #     # all_mesh=self._merge_trimesh([main_roads,major_roads,minor_roads,small_parks,big_parks])
    #     # all_mesh.export(str(Path("C:\APP\CODE\3d_city\app\services\test").joinpath("city_full.glb")), file_type="glb")
    #     logging.info("开始合并模型")
    #     all_mesh = self._merge_trimesh([coastline,river,sea,ground,main_roads, minor_roads,major_roads,big_parks,small_parks,blocks,buildings])
    #
    #     self.diagnose_mesh(mesh=ground, name="ground", export_debug=True)
    #     self.diagnose_mesh(mesh=river, name="river", export_debug=True)
    #     self.diagnose_mesh(mesh=sea, name="sea", export_debug=True)
    #
    #     # 检查所有mesh，排除错误
    #     if all_mesh is None:
    #         print("错误：all_mesh 是 None")
    #     elif len(all_mesh.vertices) == 0:
    #         print("错误：网格没有顶点")
    #     elif len(all_mesh.faces) == 0:
    #         print("错误：网格没有面")
    #     else:
    #         print(f"网格包含 {len(all_mesh.vertices)} 个顶点，{len(all_mesh.faces)} 个面")
    #         all_mesh.export("C://APP//CODE//3d_city//app//services//test//test.glb", file_type="glb")
    #     return part_meshes

    import trimesh
    import logging
    from typing import Optional

    def diagnose_mesh(self,mesh: trimesh.Trimesh, name: str = "mesh", export_debug: bool = False) -> bool:
        """
        诊断 Trimesh 对象的健康状况，输出详细信息和潜在问题。

        :param mesh: 待检查的 Trimesh 对象（可能为 None）
        :param name: 网格名称，用于输出标识
        :param export_debug: 如果为 True 且网格存在但非健康，则导出 STL 文件供调试
        :return: True 如果网格是有效的实体（is_volume=True），否则 False
        """
        if mesh is None:
            logging.error(f"❌ {name} 为 None")
            return False

        print(f"\n===== 诊断网格: {name} =====")
        print(f"顶点数: {len(mesh.vertices)}")
        print(f"面数: {len(mesh.faces)}")
        print(f"是否水密 (watertight): {mesh.is_watertight}")
        print(f"是否为实体 (volume): {mesh.is_volume}")
        print(f"体积: {mesh.volume:.6f}")
        # print(f"边界边数: {len(mesh.edges_unordered) - len(mesh.edges_unique)}")  # 粗略判断非流形边
        print(f"是否有退化面: {any(mesh.area_faces == 0)}")
        # print(f"法线一致: {mesh.face_normals_consistent}")  # 需要 trimesh 0.13+ 版本

        # 检查可能的问题
        issues = []
        if not mesh.is_watertight:
            issues.append("网格存在孔洞（非水密）")
        if mesh.volume <= 0:
            if mesh.volume < 0:
                issues.append("体积为负（法线反向）")
            else:
                issues.append("体积为零（可能是平面或退化）")
        if not mesh.is_volume:
            issues.append("不是有效实体（可能是非流形、孔洞或法线不一致）")
        if any(mesh.area_faces == 0):
            issues.append("包含退化面（面积为零）")
        if hasattr(mesh, 'face_normals_consistent') and not mesh.face_normals_consistent:
            issues.append("法线方向不一致")

        if issues:
            print("⚠️ 发现以下问题:")
            for issue in issues:
                print(f"   - {issue}")
            if export_debug:
                debug_path = f"debug_{name}.stl"
                mesh.export(debug_path)
                print(f"   - 已导出调试文件: {debug_path}")
            return False
        else:
            print("✅ 网格健康，是有效实体")
            return True

    def _upload_glb_artifacts(self, glb_paths: Dict[str, str]) -> Dict[str, str]:
        storage = get_minio_storage()
        remote_paths: Dict[str, str] = {}
        # 定义需要返回的模型key，如果不需要直接跳过即可。
        needed_keys = [ "ground", "river", "sea", "coastline","main_roads", "major_roads", "minor_roads", "buildings_divided", "blocks",
            "big_parks", "small_parks"]
        for key, value in glb_paths.items():
            if key not in needed_keys:
                continue
            if not isinstance(value, str) or not value.lower().endswith(".glb"):
                remote_paths[key] = value
                continue

            local_path = Path(value)
            if not local_path.exists():
                logging.warning("Skip upload for missing GLB: key=%s path=%s", key, local_path)
                continue

            relative_key = self._relative_asset_path(local_path)
            object_key = storage.object_name_for(relative_key)
            # storage.upload_file(local_path, object_key)

            if local_path.exists():
                self.layout_data.file_util.upload_file(local_path, relative_key)
            remote_paths[key] = relative_key.as_posix()
            logging.info("Uploaded %s to MinIO as %s", key, object_key)
        # print(remote_paths)
        return remote_paths

    def _relative_asset_path(self, local_path: Path) -> Path:
        resolved_file = local_path.resolve()
        assets_root = Path(settings.assets_storage_dir).resolve()
        try:
            return Path("assets") / resolved_file.relative_to(assets_root)
        except ValueError:
            pass
        try:
            return Path("assets") / resolved_file.relative_to(Path(self.save_dir).resolve())
        except ValueError:
            logging.warning("Falling back to filename for MinIO object: %s", local_path)
            return Path("assets") / local_path.name

    # def generate_obj(self) -> Dict:
    #     """
    #     从self.json_data生成模型（如obj等），保存到output_path。
    #     具体实现需根据原有模型生成逻辑迁移。
    #     """
    #     # logging.info("Ground区域生成: %s", self.ground_polygon)
    #     # 这里将会村春每一个模型的路径，方便后续管理和使用，其中independent_blocks_dir是blocks的每一个单独导出文件路径
    #     model_obj_paths = {
    #         "ground": str(Path(self.save_dir).joinpath("ground.obj")),
    #         "river": str(Path(self.save_dir).joinpath("river.obj")),
    #         "coastline": str(Path(self.save_dir).joinpath("coastline.obj")),
    #         "water_roads":str( Path(self.save_dir).joinpath("water_roads.obj")),
    #         "water_roads_secondary": str(Path(self.save_dir).joinpath("water_roads_secondary.obj")),
    #         "roads": str(Path(self.save_dir).joinpath("roads.obj")),
    #         "main_roads": str(Path(self.save_dir).joinpath("main_roads.obj")),
    #         "major_roads": str(Path(self.save_dir).joinpath("major_roads.obj")),
    #         "minor_roads": str(Path(self.save_dir).joinpath("minor_roads.obj")),
    #         "buildings_divided": str(Path(self.save_dir).joinpath("buildings_divided.obj")),
    #         "blocks": str(Path(self.save_dir).joinpath("blocks.obj")),
    #         "big_parks": str(Path(self.save_dir).joinpath("big_parks.obj")),
    #         "small_parks": str(Path(self.save_dir).joinpath("small_parks.obj")),
    #         "independent_blocks":str( Path(self.save_dir).joinpath("blocks.obj")),
    #         "sea": str(Path(self.save_dir).joinpath("sea.obj")),
    #         "city_glb": str(Path(self.save_dir).joinpath("city.glb")),
    #     }
    #     # Keep original polygons for trimesh GLB extrusion before in-place list mutations.
    #     layout_snapshot = {
    #         "ground_polygon": self.layout_data.ground_polygon,
    #         "river_polygon": self.layout_data.river_polygon,
    #         "sea_polygon": self.layout_data.sea_polygon,
    #         "coastline_polygon": self.layout_data.coastline_polygon,
    #         "water_road_polygon": list(self.layout_data.water_road_polygon or []),
    #         "water_secondary_road_polygon": self.layout_data.water_secondary_road_polygon,
    #         "main_exterior_interior_road_polygon": list(self.layout_data.main_exterior_interior_road_polygon or []),
    #         "main_normal_road_polygon": list(self.layout_data.main_normal_road_polygon or []),
    #         "major_exterior_interior_road_polygon": list(self.layout_data.major_exterior_interior_road_polygon or []),
    #         "major_normal_road_polygon": list(self.layout_data.major_normal_road_polygon or []),
    #         "minor_exterior_interior_road_polygon": list(self.layout_data.minor_exterior_interior_road_polygon or []),
    #         "minor_normal_road_polygon": list(self.layout_data.minor_normal_road_polygon or []),
    #         "blocks_polygon": list(self.layout_data.blocks_polygon or []),
    #         "divided_buildings_polygons": list(self.layout_data.divided_buildings_polygons or []),
    #         "big_parks_polygon": list(self.layout_data.big_parks_polygon or []),
    #         "small_parks_polygons": list(self.layout_data.small_parks_polygons or []),
    #     }
    #     os.makedirs(self.save_dir, exist_ok=True)
    #     logging.info("生成模型保存目录: %s", self.save_dir)
    #     logging.info("生成地面")
    #     ground_mesh = PolygonUtil.polygon_to_mesh(self.layout_data.ground_polygon, LevelTopBottomHeight.ground_top,
    #                                               LevelTopBottomHeight.ground_bottom)
    #     ground_mesh.compute_vertex_normals()  # 计算顶点法线以确保正确的渲染
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("ground.obj"), ground_mesh, write_vertex_normals=True)
    #     logging.info("生成河流")
    #     river_mesh = PolygonUtil.polygon_to_mesh(self.layout_data.river_polygon, LevelTopBottomHeight.river_top,
    #                                              LevelTopBottomHeight.river_bottom)
    #     river_mesh.compute_vertex_normals()
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("river.obj"), river_mesh, write_vertex_normals=True)
    #
    #     # 生成海洋区域
    #     if self.layout_data.sea_polygon:
    #         logging.info("sea: %s",  self.layout_data.sea_polygon)
    #         sea_mesh = PolygonUtil.polygon_to_mesh( self.layout_data.sea_polygon,  LevelTopBottomHeight.sea_top, LevelTopBottomHeight.sea_bottom)
    #         sea_mesh.compute_vertex_normals()
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("sea.obj"),sea_mesh,
    #                                    write_vertex_normals=True)
    #         logging.info("生成海洋")
    #     else:
    #         logging.info("没有海洋多边形数据可供导出")
    #
    #
    #
    #     # coastline_mesh = PolygonUtil.polygon_to_mesh(PolygonUtil.resize_geometry(self.water_generator.coastline,self.coastline_width,False),LevelTopBottomHeight.coastline_top, LevelTopBottomHeight.coastline_bottom ,False)
    #     coastline_mesh = PolygonUtil.polygon_to_mesh(self.layout_data.coastline_polygon, LevelTopBottomHeight.coastline_top,
    #                                                  LevelTopBottomHeight.coastline_bottom, False)
    #     coastline_mesh.compute_vertex_normals()
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("coastline.obj"), coastline_mesh,
    #                                write_vertex_normals=True)
    #
    #     water_roads_mesh = o3d.geometry.TriangleMesh()
    #     for water_road in tqdm(self.layout_data.water_road_polygon, desc="Processing Water Roads", unit="road"):
    #         water_mesh = PolygonUtil.polygon_to_mesh(water_road, LevelTopBottomHeight.main_road_top,
    #                                                  LevelTopBottomHeight.main_road_bottom)
    #         water_roads_mesh += water_mesh
    #
    #     water_secondary_mesh = PolygonUtil.polygon_to_mesh(self.layout_data.water_secondary_road_polygon,
    #                                                        LevelTopBottomHeight.main_road_top,
    #                                                        LevelTopBottomHeight.main_road_bottom)
    #     water_roads_mesh.compute_vertex_normals()
    #     water_secondary_mesh.compute_vertex_normals()
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("water_roads.obj"), water_roads_mesh,
    #                                write_vertex_normals=True)
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("water_roads_secondary.obj"), water_secondary_mesh,
    #                                write_vertex_normals=True)
    #
    #     main_road_mesh = o3d.geometry.TriangleMesh()
    #     major_road_mesh = o3d.geometry.TriangleMesh()
    #     minor_road_mesh = o3d.geometry.TriangleMesh()
    #     for exterior_interior_main_road in tqdm(self.layout_data.main_exterior_interior_road_polygon, desc="Resizing Main Roads", unit="road"):
    #         road_mesh = PolygonUtil.exterior_interior_polygon_to_mesh(exterior_interior_main_road,
    #                                                                   LevelTopBottomHeight.main_road_top,
    #                                                                   LevelTopBottomHeight.main_road_bottom)
    #         main_road_mesh += road_mesh
    #
    #     for normal_main_road in tqdm(self.layout_data.main_normal_road_polygon, desc="Processing Main Roads", unit="road"):
    #         road_mesh = PolygonUtil.polygon_to_mesh(normal_main_road, LevelTopBottomHeight.main_road_top,
    #                                                  LevelTopBottomHeight.main_road_bottom)
    #         main_road_mesh += road_mesh
    #
    #
    #     for exterior_interior_major_road in tqdm(self.layout_data.major_exterior_interior_road_polygon, desc="Resizing Major Roads", unit="road"):
    #         road_mesh = PolygonUtil.exterior_interior_polygon_to_mesh(exterior_interior_major_road,
    #                                                                   LevelTopBottomHeight.major_road_top,
    #                                                                   LevelTopBottomHeight.major_road_bottom)
    #         major_road_mesh += road_mesh
    #
    #     for normal_major_road in tqdm(self.layout_data.major_normal_road_polygon, desc="Processing Major Roads", unit="road"):
    #         road_mesh = PolygonUtil.polygon_to_mesh(normal_major_road, LevelTopBottomHeight.major_road_top,
    #                                                  LevelTopBottomHeight.major_road_bottom)
    #         major_road_mesh += road_mesh
    #
    #     for exterior_interior_minor_road in tqdm(self.layout_data.minor_exterior_interior_road_polygon, desc="Resizing Minor Roads", unit="road"):
    #         road_mesh = PolygonUtil.exterior_interior_polygon_to_mesh(exterior_interior_minor_road,
    #                                                                   LevelTopBottomHeight.minor_road_top,
    #                                                                   LevelTopBottomHeight.minor_road_bottom)
    #         minor_road_mesh += road_mesh
    #
    #     for normal_minor_road in tqdm(self.layout_data.minor_normal_road_polygon, desc="Processing Minor Roads", unit="road"):
    #         road_mesh = PolygonUtil.polygon_to_mesh(normal_minor_road, LevelTopBottomHeight.minor_road_top,
    #                                                  LevelTopBottomHeight.minor_road_bottom)
    #         minor_road_mesh += road_mesh
    #
    #     export_roads_mesh = Trimesh()
    #
    #     # for循环处理清空polygons_to_process
    #     while self.layout_data.polygons_to_process and any(self.layout_data.polygons_to_process):
    #         road = self.layout_data.polygons_to_process.pop()
    #         road_mesh = PolygonUtil.polygon_to_shape_to_mesh(road, LevelTopBottomHeight.minor_road_top,
    #                                                          LevelTopBottomHeight.minor_road_bottom)
    #         self.roads_geometry.append(road_mesh)
    #         export_roads_mesh += road_mesh  # 合并mesh到export_mesh
    #
    #
    #     export_o3d_mesh = o3d.geometry.TriangleMesh()
    #     export_o3d_mesh += main_road_mesh
    #     export_o3d_mesh += major_road_mesh
    #     export_o3d_mesh += minor_road_mesh
    #     export_o3d_mesh.compute_vertex_normals()
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("roads.obj"), export_o3d_mesh,
    #                                write_vertex_normals=True)
    #     if isinstance(main_road_mesh, o3d.geometry.TriangleMesh) and len(main_road_mesh.triangles) > 0:
    #         main_road_mesh += water_roads_mesh
    #         main_road_mesh.compute_vertex_normals()
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("main_roads.obj"), main_road_mesh,
    #                                    write_vertex_normals=True)
    #     if isinstance(major_road_mesh, o3d.geometry.TriangleMesh) and len(major_road_mesh.triangles) > 0:
    #         major_road_mesh.compute_vertex_normals()
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("major_roads.obj"), major_road_mesh,
    #                                    write_vertex_normals=True)
    #     if isinstance(minor_road_mesh, o3d.geometry.TriangleMesh) and len(minor_road_mesh.triangles) > 0:
    #         minor_road_mesh.compute_vertex_normals()
    #         minor_road_mesh += water_secondary_mesh
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("minor_roads.obj"), minor_road_mesh,
    #                                    write_vertex_normals=True)
    #     else:
    #         logging.info("没有道路流线可供导出")
    #
    #     mesh = o3d.geometry.TriangleMesh()
    #     os.makedirs(Path(self.save_dir).joinpath(f"independent_divided_buildings/"), exist_ok=True)
    #     for model in self.layout_data.divided_buildings_polygons:
    #         building_mesh=PolygonUtil.polygon_to_mesh(model,top=LevelTopBottomHeight.building_top,bottom=LevelTopBottomHeight.building_bottom)
    #         mesh+=building_mesh
    #         #     独立导出每一个分割后的建筑
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath(f"independent_divided_buildings/divided_building_{self.layout_data.divided_buildings_polygons.index(model)}.obj"),
    #                                    building_mesh,write_vertex_normals=True)
    #     mesh.compute_vertex_normals()
    #     o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("buildings_divided.obj"), mesh,write_vertex_normals=True)
    #
    #     export_blocks_mesh = o3d.geometry.TriangleMesh()
    #     os.makedirs(Path(self.save_dir).joinpath(f"independent_blocks/"), exist_ok=True)
    #     for block in layout_snapshot["blocks_polygon"]:
    #         block_mesh = PolygonUtil.polygon_to_mesh(block,LevelTopBottomHeight.blocks_top,LevelTopBottomHeight.blocks_bottom)
    #         self.blocks_geometry.append(block_mesh)
    #         # 每一个 block单独导出 ./export/output/independent_blocks/
    #         # block_mesh.export(Path(f"./export/output/independent_blocks/block_{len(self.blocks_geometry)}.obj"))
    #
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath(f"independent_blocks/block_{len(self.blocks_geometry)}.obj"), block_mesh, write_vertex_normals=True)
    #
    #         export_blocks_mesh += block_mesh
    #
    #     if export_blocks_mesh and len(export_blocks_mesh.triangles) > 0:
    #         export_blocks_mesh.compute_vertex_normals()
    #         o3d.io.write_triangle_mesh(Path(self.save_dir).joinpath("blocks.obj"), export_blocks_mesh, write_vertex_normals=True)
    #     else:
    #         logging.info("没有可供导出的 blocks")
    #
    #     big_park_color = [0.0, 0.8, 0.0]  # 绿色
    #     small_park_color = [0.0, 0.6, 0.0]  # 稍暗的绿色
    #
    #     # 创建大公园的网格
    #     export_big_parks_mesh = Trimesh()
    #     big_parks_list=[]
    #     os.makedirs(Path(self.save_dir).joinpath(f"independent_big_parks/"), exist_ok=True)
    #     for park in self.layout_data.big_parks_polygon:
    #         park_mesh = PolygonUtil.polygon_to_shape_to_mesh(park, LevelTopBottomHeight.big_park_top,
    #                                                          LevelTopBottomHeight.big_park_bottom)
    #         big_parks_list.append(park_mesh)
    #         # os.makedirs(Path(self.save_dir).joinpath(f"/models/independent_big_parks"), exist_ok=True)
    #         park_mesh.export(Path(self.save_dir).joinpath(f"independent_big_parks/big_parks_{len(big_parks_list)}.obj"))
    #
    #         export_big_parks_mesh += park_mesh
    #     export_small_parks_mesh = Trimesh()
    #     small_parks_list=[]
    #     os.makedirs(Path(self.save_dir).joinpath(f"independent_small_parks"), exist_ok=True)
    #     for idx,park in enumerate(self.layout_data.small_parks_polygons):
    #         park_mesh = PolygonUtil.polygon_to_shape_to_mesh(park, LevelTopBottomHeight.small_park_top,
    #                                                          LevelTopBottomHeight.small_park_bottom)
    #         # small_parks_list.append(park_mesh)
    #
    #         park_mesh.export(Path(self.save_dir).joinpath(f"independent_small_parks/small_parks_{idx}.obj"))
    #         export_small_parks_mesh += park_mesh
    #         # 创建 Open3D 网格并赋予颜色
    #     export_o3d_big_parks_mesh = o3d.geometry.TriangleMesh()
    #     export_o3d_small_parks_mesh = o3d.geometry.TriangleMesh()
    #     if export_big_parks_mesh and len(export_big_parks_mesh.faces) > 0:
    #         export_o3d_big_parks_mesh.vertices = o3d.utility.Vector3dVector(export_big_parks_mesh.vertices)
    #         export_o3d_big_parks_mesh.triangles = o3d.utility.Vector3iVector(export_big_parks_mesh.faces)
    #         export_o3d_big_parks_mesh.compute_vertex_normals()
    #         export_o3d_big_parks_mesh.paint_uniform_color(big_park_color)  # 设置颜色
    #         export_big_parks_mesh = Trimesh(vertices=np.asarray(export_o3d_big_parks_mesh.vertices),
    #                                         faces=np.asarray(export_o3d_big_parks_mesh.triangles))
    #         export_big_parks_mesh.export(Path(self.save_dir).joinpath("big_parks.obj"))
    #     else:
    #         logging.info("没有可供导出的大公园")
    #
    #     if export_small_parks_mesh and len(export_small_parks_mesh.faces) > 0:
    #         export_o3d_small_parks_mesh.vertices = o3d.utility.Vector3dVector(export_small_parks_mesh.vertices)
    #         export_o3d_small_parks_mesh.triangles = o3d.utility.Vector3iVector(export_small_parks_mesh.faces)
    #         export_o3d_small_parks_mesh.compute_vertex_normals()
    #         export_o3d_small_parks_mesh.paint_uniform_color(small_park_color)  # 设置颜色
    #         export_small_parks_mesh = Trimesh(vertices=np.asarray(export_o3d_small_parks_mesh.vertices),
    #                                           faces=np.asarray(export_o3d_small_parks_mesh.triangles))
    #         export_small_parks_mesh.export(Path(self.save_dir).joinpath("small_parks.obj"))
    #     else:
    #         logging.info("没有可供导出的小公园")
    #
    #
    #     # model_obj_paths = self._export_city_glb(model_obj_paths)
    #     # OBJ files are still written to disk, and GLBs are exported via polygon extrusion first.
    #     return self._export_part_glbs(model_obj_paths, layout_snapshot=layout_snapshot)
@dataclass
class LevelTopBottomHeight:
    # Ground is the absolute lowest layer.
    ground_bottom: int = 0
    ground_top: int = 2

    # Keep sea/river/roads/parks/blocks roughly coplanar.
    sea_bottom: int = 1
    sea_top: int = 2

    coastline_bottom: int = 1
    coastline_top: int = 2

    river_bottom: int = 1
    river_top: int = 2

    main_road_bottom: int = 2
    main_road_top: int = 3

    major_road_bottom: int = 2
    major_road_top: int = 3

    minor_road_bottom: int = 2
    minor_road_top: int = 3

    big_park_bottom: int = 2
    big_park_top: int = 3

    blocks_bottom: int = 2
    blocks_top: int = 3

    # Buildings are slightly higher to match urban perception.
    building_bottom: int = 3
    building_top: int = 6

    small_park_bottom: int = 2
    small_park_top: int = 3

