import json
import logging
import os
import random
from pathlib import Path

from tqdm import tqdm

from app.schemas.layout import LayoutParams
from app.services.procgen_python.custom_struct import ALLParams, Vector, \
    MainMajorMinorStreamlineParams, PolygonParams, NoiseStreamlineParams, WaterParams
from app.services.procgen_python.custom_struct.json_layout import json_layout
from app.services.procgen_python.service.buildings import Buildings
from app.services.procgen_python.service.graph import Graph
from app.services.procgen_python.service.integrator import RK4Integrator
from app.services.procgen_python.service.polygon_finder import PolygonFinder
from app.services.procgen_python.service.polygon_util import PolygonUtil
from app.services.procgen_python.service.streamlines import StreamlineGenerator
from app.services.procgen_python.service.tensor_field import TensorField, NoiseParams
# from app.services.procgen_python.service.noise_params import NoiseParams
from app.services.procgen_python.service.water_generator import WaterGenerator

# 确保日志目录存在
os.makedirs('./log', exist_ok=True)

# 配置日志
logging.basicConfig(
    filename='./log/app.log',  # 日志文件名
    filemode='a',  # 如果文件不存在则创建，存在则覆盖
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',  # 日志格式
encoding='utf-8'
)

# 使用日志
logging.info('这是一个信息日志')
logging.warning('这是一个警告日志')
logging.error('这是一个错误日志')




noiseParamsPlaceholder: NoiseParams = NoiseParams(
    global_noise=False,
    noise_size_park=20,
    noise_angle_park=90,
    noise_size_global=30,
    noise_angle_global=20
)
from dataclasses import dataclass

@dataclass    
class RoadsSize:
    main_road_width_multiplier = 6.0  # 例如，主要道路更宽
    major_road_width_multiplier = 3.0 # 主干道宽度
    minor_road_width_multiplier = 2.0 # 次要道路较窄    

class GenerationStageError(Exception):
    def __init__(self, stage, message=None):
        self.stage = stage
        self.message = message or f"{stage} 阶段生成出错"
        super().__init__(self.message)

class Generator:
    def __init__(self, params_var:LayoutParams,noise_params_input: NoiseParams = noiseParamsPlaceholder,dir="./export/output"):

        # 布局信息存储
        self.layout = None

        # 海岸线宽度设置
        self.water_secondary_mesh = None
        self.water_roads_mesh = None
        self.coastline_width = params_var.map.water.coastline_width
        #   从文件中读取参数，赋予世界坐标系和原点
        self.buildings_geometry =[]
        self.buildings_to_process:list[list[Vector]] = []
        self.blocks_geometry = []
        self.roads_geometry = []
        self.world_dimensions = Vector(params_var.world_dimensions.x, params_var.world_dimensions.y)
        self.origin = Vector(params_var.origin.x, params_var.origin.y)
        self.params: ALLParams = params_var
        self.noise_params = noise_params_input
        self.all_streamlines:list=[]
        self.save_dir=dir
        self.main_params: MainMajorMinorStreamlineParams = MainMajorMinorStreamlineParams(
            dsep=self.params.map.main.dsep,
            dtest=self.params.map.main.dtest,
            dstep=self.params.map.main.dev_params.dstep,
            dcircle_join=self.params.map.main.dev_params.dcircle_join,
            dlookahead=self.params.map.main.dev_params.dlookahead,
            join_angle=self.params.map.main.dev_params.join_angle,
            path_iterations=self.params.map.main.dev_params.path_iterations,
            seed_tries=self.params.map.main.dev_params.seed_tries,
            simplify_tolerance=self.params.map.main.dev_params.simplify_tolerance,
            collide_early=self.params.map.main.dev_params.collide_early,
        )

        self.major_params: MainMajorMinorStreamlineParams = MainMajorMinorStreamlineParams(
            dsep=self.params.map.major.dsep,
            dtest=self.params.map.major.dtest,
            dstep=self.params.map.major.dev_params.dstep,
            dcircle_join=self.params.map.major.dev_params.dcircle_join,
            dlookahead=self.params.map.major.dev_params.dlookahead,
            join_angle=self.params.map.major.dev_params.join_angle,
            path_iterations=self.params.map.major.dev_params.path_iterations,
            seed_tries=self.params.map.major.dev_params.seed_tries,
            simplify_tolerance=self.params.map.major.dev_params.simplify_tolerance,
            collide_early=self.params.map.major.dev_params.collide_early,
        )
        self.minor_params: MainMajorMinorStreamlineParams = MainMajorMinorStreamlineParams(
            dsep=self.params.map.minor.dsep,
            dtest=self.params.map.minor.dtest,
            dstep=self.params.map.minor.dev_params.dstep,
            dcircle_join=self.params.map.minor.dev_params.dcircle_join,
            dlookahead=self.params.map.minor.dev_params.dlookahead,
            join_angle=self.params.map.minor.dev_params.join_angle,
            path_iterations=self.params.map.minor.dev_params.path_iterations,
            seed_tries=self.params.map.minor.dev_params.seed_tries,
            simplify_tolerance=self.params.map.minor.dev_params.simplify_tolerance,
            collide_early=self.params.map.minor.dev_params.collide_early,
        )
        self.water_params = WaterParams(
            dsep=self.params.map.water.dev_params.dsep,
            dtest=self.params.map.water.dev_params.dtest,
            dstep=self.params.map.water.dev_params.dstep,
            dcircle_join=self.params.map.water.dev_params.dcircle_join,
            dlookahead=self.params.map.water.dev_params.dlookahead,
            join_angle=self.params.map.water.dev_params.join_angle,
            path_iterations=self.params.map.water.dev_params.path_iterations,
            seed_tries=self.params.map.water.dev_params.seed_tries,
            simplify_tolerance=self.params.map.water.simplify_tolerance,
            collide_early=0,
            coast_noise=NoiseStreamlineParams(
                noise_enabled=self.params.map.water.coastline.noise_enabled,
                noise_size=self.params.map.water.coastline.noise_size,
                noise_angle=self.params.map.water.coastline.noise_angle
            ),
            river_noise=NoiseStreamlineParams(
                noise_enabled=self.params.map.water.river.noise_enabled,
                noise_size=self.params.map.water.river.noise_size,
                noise_angle=self.params.map.water.river.noise_angle
            ),
            river_bank_size=self.params.map.water.river_bank_size,
            river_size=self.params.map.water.river_size
        )

        self.polygons_to_process: list[list[Vector]] = []
        self.process = None
        self.firstGenerate = True
        # 存在一个是否忽略河流水域的选项，这里设置为True，因此可以形成跨河流道路
        self.tensor_field = TensorField(self.noise_params,world_dimensions=self.world_dimensions,ignore_river=False)
        self.water_integrator = RK4Integrator(self.tensor_field, self.water_params)
        self.main_integrator = RK4Integrator(self.tensor_field, self.main_params)
        self.major_integrator = RK4Integrator(self.tensor_field, self.major_params)
        self.minor_integrator = RK4Integrator(self.tensor_field, self.minor_params)

        self.water_generator: WaterGenerator = WaterGenerator(tensor_field=self.tensor_field,
                                                              integrator=self.water_integrator, origin=self.origin,
                                                              world_dimensions=self.world_dimensions,
                                                              params=self.water_params)

        self._animate = False
        self.redraw = True

        # Initialize buildings
        self.buildings = None

        self.ground = [
            Vector(0, 0), Vector(0, self.world_dimensions.y),Vector(self.world_dimensions.x, self.world_dimensions.y),Vector(self.world_dimensions.x, 0),
        ]

        self.sea: list[Vector] = []
        self.coastline: list[Vector] = []

        self.river: list[Vector] = []
        self.main_roads: list[list[Vector]] = []
        self.major_roads: list[list[Vector]] = []
        self.minor_roads: list[list[Vector]] = []
        self.big_parks = []
        self.small_parks = []
        self.intersections = []
        self.blocks: list[list[Vector]] = []
        self.buildings_list:list[Buildings]= []
        self.main_streamlines_generator = StreamlineGenerator(self.main_integrator, self.origin, self.world_dimensions, self.main_params)
        self.major_streamlines_generator = StreamlineGenerator(self.major_integrator, self.origin, self.world_dimensions, self.major_params)
        self.minor_streamlines_generator = StreamlineGenerator(self.minor_integrator, self.origin, self.world_dimensions, self.minor_params)
        self.river_secondary_road = []
        self.sea_polygon = []
        self.river_polygon = []

    @staticmethod
    def _serialize_point(point: Vector) -> dict:
        return {"x": point.x, "y": point.y}

    @classmethod
    def _serialize_polyline(cls, polyline: list[Vector]) -> list[dict]:
        return [cls._serialize_point(point) for point in polyline]

    @classmethod
    def _serialize_polylines(cls, polylines: list[list[Vector]]) -> list[list[dict]]:
        return [cls._serialize_polyline(polyline) for polyline in polylines]

    def _write_artifact(self, filename: str, payload: dict) -> None:
        path = Path(self.save_dir).joinpath(filename)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    @staticmethod
    def _deserialize_point(data: dict) -> Vector:
        return Vector(data.get("x", 0), data.get("y", 0))

    @classmethod
    def _deserialize_polyline(cls, data: list[dict]) -> list[Vector]:
        return [cls._deserialize_point(item) for item in data]

    @classmethod
    def _deserialize_polylines(cls, data: list[list[dict]]) -> list[list[Vector]]:
        return [cls._deserialize_polyline(item) for item in data]




    def generate_layout_stage_0(self):
        # 添加基础场
        logging.info("添加基础场")
        if not hasattr(self.params, 'tensor_field') or not hasattr(self.params.tensor_field, 'grids'):
            logging.error("参数缺少 tensor_field.grids，程序退出")
            raise GenerationStageError("基础场阶段", "参数缺少 tensor_field.grids")
        for grid in self.params.tensor_field.grids:
            self.tensor_field.add_grid(Vector(grid.x, grid.y), grid.size, grid.decay, grid.theta)
        for radial  in self.params.tensor_field.radials:
            self.tensor_field.add_radial(Vector(radial.x, radial.y),radial.size,radial.decay)
        if not self.tensor_field:
            logging.error("基础场生成失败，程序退出")
            raise GenerationStageError("基础场阶段", "基础场生成失败")
        logging.info(f"Radials num: {len(self.params.tensor_field.radials)},")

    # 生成海岸线
    def generate_layout_stage_1_water_line(self):
        try:
            self.water_generator.create_coast()
            self.water_generator.create_river()
        except Exception as e:
            logging.error(f"海岸线/河流生成失败: {e}")
            raise GenerationStageError("水体线阶段", f"海岸线/河流生成失败: {e}")

    def generate_layout_stage_2_water_polygon(self):
        self.sea_polygon = self.water_generator.sea_polygon
        self.river_polygon = self.water_generator.river_polygon
        self.river_secondary_road = self.water_generator.river_secondary_road
        if not self.river_secondary_road:
            logging.info("次要河流生成失败，程序退出")
            raise GenerationStageError("水体多边形阶段", "次要河流生成失败")

    def generate_layout_stage_3_main_and_major_roads(self):
        # 生成主要道路
        self.tensor_field.ignore_river=True
        self.main_roads = self.generate_main_roads()
        if not self.main_roads:
            logging.info("主要道路生成失败，程序退出")
            raise GenerationStageError("主要道路阶段", "主要道路生成失败")
        else:
            logging.info("主要道路生成成功，开始可视化")
        # 生成主干道
        self.major_roads = self.generate_major_roads()
        self.tensor_field.ignore_river=False

    def generate_layout_stage_4_big_parks(self):
        self.add_parks()
        if not self.major_roads:
            logging.info("主干道生成失败，程序退出")
            raise GenerationStageError("主干道阶段", "主干道生成失败")
        else:
            logging.info("主干道生成成功")
        self.tensor_field.parks=self.big_parks

    def generate_layout_stage_5_minor_roads(self):
        # 生成次要道路
        self.minor_roads = self.generate_minor_roads()
        if not self.minor_roads:
            logging.info("次要道路生成失败，程序退出")
            raise GenerationStageError("次要道路阶段", "次要道路生成失败")
        else:
            logging.info("次要道路生成成功，开始可视化")
        # 合并所有流线
        logging.info("合并所有流线")
        self.all_streamlines=self.major_roads + self.main_roads + self.minor_roads+self.water_generator.get_streamlines_with_secondary_road()

    def generate_layout_stage_6_small_parks(self):
        # 设置重绘标志
        self.redraw = True
        try:
            self.add_parks()
        except Exception as e:
            logging.error(f"小公园生成失败: {e}")
            raise GenerationStageError("小公园阶段", f"小公园生成失败: {e}")
        logging.info("张量场可视化")
        try:
            self.tensor_field.visualize(Path(self.save_dir))
        except Exception as e:
            logging.error(f"张量场可视化失败: {e}")
            raise GenerationStageError("小公园阶段", f"张量场可视化失败: {e}")
        logging.info("生成结束")

    def generate_layout_stage_7_polygon(self):
        # 海岸线需要扩展（resize-space为两侧扩展宽度）
        try:
            coastline_polygon = PolygonUtil.resize_geometry(self.water_generator.coastline, self.coastline_width, False)
        except Exception as e:
            logging.error(f"海岸线多边形扩展失败: {e}")
            raise GenerationStageError("多边形阶段", f"海岸线多边形扩展失败: {e}")
        if not self.minor_roads or not self.major_roads or not self.main_roads:
            logging.info("道路流线为空，无法处理")
            raise GenerationStageError("多边形阶段", "道路流线为空，无法处理")

        self.polygons_to_process = []
        roads = self.minor_roads + self.major_roads + self.main_roads

        water_stream_lines = self.water_generator.all_streamlines_simple
        resized_water_road_list = []
        for water_road in tqdm(water_stream_lines, desc="Processing Water Roads", unit="road"):
            # 确保水路流线不为空
            if not water_road:
                logging.warning("水路流线为空，跳过处理")
                continue
            resized_water_road = PolygonUtil.resize_geometry(water_road, RoadsSize.minor_road_width_multiplier * 0.1,
                                                             False)
            resized_water_road_list.append(resized_water_road)
        resized_water_secondary_road = PolygonUtil.resize_geometry(self.river_secondary_road,
                                                                   RoadsSize.minor_road_width_multiplier * 0.1, False)

        main_road_width_multiplier = RoadsSize.main_road_width_multiplier
        major_road_width_multiplier = RoadsSize.major_road_width_multiplier  # 主干道宽度
        minor_road_width_multiplier = RoadsSize.minor_road_width_multiplier  # 次要道路较窄

        exterior_interior_main_road_list = []
        normal_main_road_list = []


        # 处理主要道路 (Main Roads)
        for road in tqdm(self.main_roads, desc="Resizing Main Roads", unit="road"):
            is_closed = PolygonUtil.is_closed(road)
            if is_closed:
                exterior_interior_road = PolygonUtil.resize_geometry_closed(road,
                                                                            main_road_width_multiplier * self.params.zoom)
                exterior_interior_main_road_list.append(exterior_interior_road)

                # self.polygons_to_process.append(exterior_interior_road)
            else:
                resized_road = PolygonUtil.resize_geometry(road, main_road_width_multiplier * self.params.zoom, False)
                normal_main_road_list.append(resized_road)
                self.polygons_to_process.append(resized_road)

        exterior_interior_major_road_list = []
        normal_major_road_list = []

        # 处理主干道 (Major Roads)
        logging.info("Resizing major roads...")
        for road in tqdm(self.major_roads, desc="Resizing Major Roads", unit="road"):
            is_closed = PolygonUtil.is_closed(road)
            if is_closed:

                exterior_interior_road = PolygonUtil.resize_geometry_closed(road,
                                                                            major_road_width_multiplier * self.params.zoom)
                exterior_interior_major_road_list.append(exterior_interior_road)

                # road_mesh = PolygonUtil.exterior_interior_polygon_to_mesh(exterior_interior_road,
                #                                                           LevelTopBottomHeight.major_road_top,
                #                                                           LevelTopBottomHeight.major_road_bottom)
                # # self.polygons_to_process.append(exterior_interior_road)
            else:
                resized_road = PolygonUtil.resize_geometry(road, major_road_width_multiplier * self.params.zoom, False)
                normal_major_road_list.append(resized_road)
                self.polygons_to_process.append(resized_road)

        exterior_interior_minor_road_list = []
        normal_minor_road_list = []

        # 处理次要道路 (Minor Roads)
        logging.info("Resizing minor roads...")
        for road in tqdm(self.minor_roads, desc="Resizing Minor Roads", unit="road"):
            is_closed = PolygonUtil.is_closed(road)
            if is_closed:
                exterior_interior_road = PolygonUtil.resize_geometry_closed(road,
                                                                            minor_road_width_multiplier * 0.1)
                exterior_interior_minor_road_list.append(exterior_interior_road)
                # road_mesh = PolygonUtil.exterior_interior_polygon_to_mesh(exterior_interior_road,
                #                                                           LevelTopBottomHeight.minor_road_top,
                #                                                           LevelTopBottomHeight.minor_road_bottom)

            else:
                resized_road = PolygonUtil.resize_geometry(road, minor_road_width_multiplier * 0.1, False)
                self.polygons_to_process.append(resized_road)
                normal_minor_road_list.append(resized_road)

        self.buildings = Buildings(tensor_field=self.tensor_field, dstep=self.minor_params.dstep,
                                   all_streamlines=self.all_streamlines, building_params=self.params.map.buildings,
                                   animate=self._animate)

        logging.info("buildings.get_blocks()")
        self.blocks = self.buildings.get_blocks()
        divided_polygons = self.buildings.polygon_finder.get_divided_polygons()
        if not self.blocks:
            logging.info("Blocks 结果为空")
        self.layout=json_layout(json_path="",origin=self.origin,world_dimensions=self.world_dimensions,small_parks_polygons=self.small_parks,big_parks_polygon=self.big_parks,divided_buildings_polygons=divided_polygons,blocks_polygon=self.blocks,polygons_to_process=self.polygons_to_process,minor_exterior_interior_road_polygon=exterior_interior_minor_road_list,minor_normal_road_polygon=normal_minor_road_list,major_exterior_interior_road_polygon=exterior_interior_major_road_list,major_normal_road_polygon=normal_major_road_list,main_exterior_interior_road_polygon=exterior_interior_main_road_list,main_normal_road_polygon=normal_main_road_list,water_secondary_road_polygon=resized_water_secondary_road,water_road_polygon=resized_water_road_list,coastline_polygon=coastline_polygon,ground_polygon=self.ground,river_polygon=self.water_generator.river_polygon,sea_polygon=self.water_generator.sea_polygon)

        # self.polygons_to_process = self.blocks[:]

    def generate_layout_stage_8_export_svg_json(self):
        svg_output_path = Path(self.save_dir).joinpath("layout.svg")
        self.layout.generate_complete_svg(svg_output_path)
        logging.info("Generating layout stage 8 export")
        json_output_path = Path(self.save_dir).joinpath("layout.json")
        self.layout.save_json(json_output_path)

    def export_streamlines_artifact(self) -> None:
        payload = {
            "origin": self._serialize_point(self.origin),
            "world_dimensions": self._serialize_point(self.world_dimensions),
            "roads": {
                "main": self._serialize_polylines(self.main_roads),
                "major": self._serialize_polylines(self.major_roads),
                "minor": self._serialize_polylines(self.minor_roads),
            },
            "water": {
                "coastline": self._serialize_polyline(self.water_generator.coastline),
                "river": self._serialize_polyline(self.water_generator.river_polygon),
                "river_secondary": self._serialize_polyline(self.river_secondary_road),
                "streamlines": self._serialize_polylines(self.water_generator.all_streamlines_simple),
            },
            "all_streamlines": self._serialize_polylines(self.all_streamlines),
        }
        self._write_artifact("streamlines.json", payload)

    # 生成所有 block 的 SVG 文件
    def export_blocks_svg(self, blocks):
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom.minidom import parseString

        svg = Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(self.world_dimensions.x),
            height=str(self.world_dimensions.y),
            viewBox=f"{self.origin.x} {self.origin.y} {self.world_dimensions.x} {self.world_dimensions.y}",
            preserveAspectRatio="xMidYMid meet",
        )
        for idx, block in enumerate(blocks):
            block_id = f"block_{idx + 1}"
            group = SubElement(svg, "g", id=block_id)
            SubElement(group, "polygon", points=" ".join(f"{p.x},{p.y}" for p in block), fill="black")

        svg_string = parseString(tostring(svg)).toprettyxml(indent="  ")
        with open(Path(self.save_dir).joinpath("blocks.svg"), "w", encoding="utf-8") as svg_file:
            svg_file.write(svg_string)

    def export_polygons_json(self) -> None:
        payload = {
            "origin": self._serialize_point(self.origin),
            "world_dimensions": self._serialize_point(self.world_dimensions),
            "ground": self._serialize_polyline(self.ground),
            "sea": self._serialize_polyline(self.sea_polygon),
            "river": self._serialize_polyline(self.river_polygon),
            "coastline": self._serialize_polyline(self.water_generator.coastline),
            "parks": {
                "big": self._serialize_polylines(self.big_parks),
                "small": self._serialize_polylines(self.small_parks),
            },
            "blocks": self._serialize_polylines(self.blocks),
        }
        self._write_artifact("polygons.json", payload)


    def generate_main_roads(self) -> list:
        logging.info("生成主要道路")
        self.main_streamlines_generator.add_existing_streamlines(self.water_generator)
        self.main_streamlines_generator.create_all_streamlines()
        return self.main_streamlines_generator.allStreamlinesSimple

    def generate_major_roads(self) -> list:
        logging.info("生成主干道")
        self.major_streamlines_generator.add_existing_streamlines(self.water_generator)
        self.major_streamlines_generator.add_existing_streamlines(self.main_streamlines_generator)
        self.major_streamlines_generator.create_all_streamlines()
        return self.major_streamlines_generator.allStreamlinesSimple

    def generate_minor_roads(self) -> list:
        logging.info("生成次要道路")
        self.minor_streamlines_generator.add_existing_streamlines(self.water_generator)
        self.minor_streamlines_generator.add_existing_streamlines(self.main_streamlines_generator)
        self.minor_streamlines_generator.add_existing_streamlines(self.major_streamlines_generator)
        self.minor_streamlines_generator.create_all_streamlines()
        return self.minor_streamlines_generator.allStreamlinesSimple

    def add_parks(self):

        g = Graph(self.main_roads + self.major_roads + self.minor_roads, self.minor_params.dstep)
        self.intersections = g.intersections

        # 2. 用 PolygonFinder 找出所有封闭多边形
        polygon_finder = PolygonFinder(
            g.nodes,
            PolygonParams(
                max_length=20,
                min_area=1,
                shrink_spacing=3,
                chance_no_divide=1
            ),
            self.tensor_field
        )
        polygon_finder.find_polygons()

        polygons = polygon_finder.polygons

        if len(self.minor_roads) == 0:
            # 只选大公园
            if len(polygons) > self.params.map.parks.num_big_parks:
                if self.params.map.parks.cluster_big_parks:
                    park_index = random.randint(0, len(polygons) - self.params.map.parks.num_big_parks)
                    self.big_parks = polygons[park_index:park_index + self.params.map.parks.num_big_parks]
                else:
                    for _ in range(self.params.map.parks.num_big_parks):
                        park_index = random.randint(0, len(polygons) - 1)
                        self.big_parks.append(polygons[park_index])
            else:
                self.big_parks = polygons
        else:
            # 只选小公园
            logging.info("次要道路存在，选择小公园")
            for _ in range(self.params.map.parks.num_small_parks):
                park_index = random.randint(0, len(polygons) - 1)
                self.small_parks.append(polygons[park_index])

        # 4. 同步到张量场
        logging.info("同步到张量场")
        logging.info("大公园数量: %d, 小公园数量: %d", len(self.big_parks), len(self.small_parks))
        self.tensor_field.parks = self.big_parks + self.small_parks
