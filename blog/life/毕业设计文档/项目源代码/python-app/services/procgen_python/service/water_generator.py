import logging
import random
from typing import List

from .integrator import FieldIntegrator
from .polygon_util import PolygonUtil
from .streamlines import StreamlineGenerator
from .tensor_field import TensorField
from app.services.procgen_python.custom_struct import Vector
from app.services.procgen_python.custom_struct.streamline_interface import WaterParams


class WaterGenerator(StreamlineGenerator):
    """
    整合折线以创建海岸线和河流，具有可控噪声
    """
    def __init__(self, integrator: FieldIntegrator, origin: Vector, world_dimensions: Vector,
                 params: WaterParams, tensor_field: TensorField):
        super().__init__(integrator, origin, world_dimensions, params)

        self.TRIES = 100
        self.coastline_major = True
        self.coastline:List[Vector] = []  # 带噪声的线
        self.sea_polygon:List[Vector] = []  # 使用屏幕矩形和简化的道路
        self.river_polygon:List[Vector] = []  # 简化的
        self.river_secondary_road = []
        self.tensor_field = tensor_field
        self.params = params
        self.all_streamlines: List[List[Vector]] = []
        self.streamlines_major: List[List[Vector]] = []
        self.streamlines_minor: List[List[Vector]] = []
        self.all_streamlines_simple: List[List[Vector]] = []


    def create_coast(self) -> List[List[Vector]]:
        """创建海岸"""
        coast_streamline:list[Vector] = []
        seed = None
        major = None

        if self.params.coast_noise.noise_enabled:
            self.tensor_field.enable_global_noise(self.params.coast_noise.noise_angle, self.params.coast_noise.noise_size)
        logging.info("开始创建海岸线")
        for i in range(self.TRIES):
            major = random.random() < 0.5
            seed = self.get_seed(major)
            logging.info("种子点", seed)
            logging.info("尝试生成流线")
            coast_streamline = self.extend_streamline(self.integrate_streamline(seed, major))
            logging.info("尝试到边缘")
            if self.reaches_edges(coast_streamline):
                print("到达边缘",self.reaches_edges(coast_streamline))
                break
        logging.info("完成海岸线创建")
        self.tensor_field.disable_global_noise()
        # 简化海岸线
        self.coastline = self.simplify_streamline(coast_streamline)
        self.coastline_major = major
        
        road = self.simplify_streamline(coast_streamline)
        self.sea_polygon = self.get_sea_polygon(road)
    
      
        self.all_streamlines_simple.append(road)
        self.tensor_field.sea = self.sea_polygon

        # 创建中间样本
        complex_line = self.complexify_streamline(road)
        self.grid(major).add_polyline(complex_line)
        self.streamlines(major).append(complex_line)
        self.all_streamlines.append(complex_line)
        # 将海岸线添加到所有流线中
        return self.all_streamlines

    def create_river(self) -> list[list[Vector]] | None:
        """创建河流"""
        river_streamline = None
        # seed = None

        # 在进行边缘检查集成时需要忽略海洋
        old_sea = self.tensor_field.sea
        self.tensor_field.sea = []
        
        if self.params.river_noise.noise_enabled:
            self.tensor_field.enable_global_noise(self.params.river_noise.noise_angle, self.params.river_noise.noise_size)
            
        for i in range(self.TRIES):
            seed = self.get_seed(not self.coastline_major)
            river_streamline = self.extend_streamline(self.integrate_streamline(seed, not self.coastline_major))

            if self.reaches_edges(river_streamline):
                break
            elif i == self.TRIES - 1:
                logging.error('无法找到到达边缘的河流')
                
        self.tensor_field.sea = old_sea
        self.tensor_field.disable_global_noise()

        # 创建河流道路
        expanded_noisy = self.complexify_streamline(PolygonUtil.resize_geometry(river_streamline, self.params.river_size, False))
        # 扩展河流宽度（河宽减去河道）
        # 补充对河流的简化
        temp_river_streamline=self.simplify_streamline(river_streamline)
        self.river_polygon = PolygonUtil.resize_geometry(
            temp_river_streamline, self.params.river_size - self.params.river_bank_size, False)
        # self.tensor_field.river = self.river_polygon
        # 确保river_polygon[0]在屏幕外
        first_off_screen = next((i for i, v in enumerate(expanded_noisy) if self.vector_off_screen(v)), -1)
        for i in range(first_off_screen):
            expanded_noisy.append(expanded_noisy.pop(0))

        # 创建河流道路
        river_split_poly = self.get_sea_polygon(river_streamline)
        road1 = [v for v in expanded_noisy if not PolygonUtil.inside_polygon(v, self.sea_polygon)
                and not self.vector_off_screen(v)
                and PolygonUtil.inside_polygon(v, river_split_poly)]
        road1_simple = self.simplify_streamline(road1)
        
        road2 = [v for v in expanded_noisy if not PolygonUtil.inside_polygon(v, self.sea_polygon)
                and not self.vector_off_screen(v)
                and not PolygonUtil.inside_polygon(v, river_split_poly)]
        road2_simple = self.simplify_streamline(road2)

        if len(road1) == 0 or len(road2) == 0:
            return None

        if (road1[0].distance_to_squared(road2[0]) < 
                road1[0].distance_to_squared(road2[len(road2) - 1])):
            road2_simple.reverse()

        self.tensor_field.river = road1_simple + road2_simple

        # 道路 1
        self.all_streamlines_simple.append(road1_simple)
        self.river_secondary_road = road2_simple

        self.grid(not self.coastline_major).add_polyline(road1)
        self.grid(not self.coastline_major).add_polyline(road2)
        self.streamlines(not self.coastline_major).append(road1)
        self.streamlines(not self.coastline_major).append(road2)
        self.all_streamlines.append(road1)
        self.all_streamlines.append(road2)
        return self.all_streamlines

    def manually_add_streamline(self, s: List[Vector], major: bool) -> None:
        
        self.all_streamlines_simple.append(s)
        # 创建中间样本
        complex_line = self.complexify_streamline(s)
        self.grid(major).add_polyline(complex_line)
        self.streamlines(major).append(complex_line)
        self.all_streamlines.append(complex_line)

    def get_sea_polygon(self, polyline: List[Vector]) -> List[Vector]:
        """
        可能会反转输入数组
        """
        return PolygonUtil.line_rectangle_polygon_intersection(self.origin, self.world_dimensions, polyline)

    def complexify_streamline(self, s: List[Vector]) -> List[Vector]:
        """
        在流线中插入样本，直到间距为dstep
        """
        out = []
        for i in range(len(s) - 1):
            out.extend(self.complexify_streamline_recursive(s[i], s[i + 1]))
        return out

    def complexify_streamline_recursive(self, v1: Vector, v2: Vector) -> List[Vector]:
        """递归处理复杂流线"""
        if v1.distance_to_squared(v2) <= self.params_sq.dstep:
            return [v1, v2]
            
        d = v2.clone().sub(v1)
        halfway = v1.clone().add(d.multiply_scalar(0.5))

        complex_line = self.complexify_streamline_recursive(v1, halfway)
        complex_line.extend(self.complexify_streamline_recursive(halfway, v2))
        return complex_line

    def extend_streamline(self, streamline: list[Vector]) -> list[Vector]:
        logging.info("延长流线")
        if len(streamline) >= 2:
            logging.info("流线数组大于2")
            streamline.insert(
                0,
                streamline[0].clone().add(
                    streamline[0].clone().sub(streamline[1]).set_length(self.params.dstep * 5)
                )
            )
        else:
            logging.info("流线数组小于2")
        logging.info("追加流线")
        streamline.append(
            streamline[-1].clone().add(
                streamline[-1].clone().sub(streamline[-2]).set_length(self.params.dstep * 5)
            )
        )
        logging.info("返回流线")
        return streamline

    def reaches_edges(self, streamline: List[Vector]) -> bool:
        """检查流线是否到达边缘"""
        return (self.vector_off_screen(streamline[0]) and 
                self.vector_off_screen(streamline[len(streamline) - 1]))

    def vector_off_screen(self, v: Vector) -> bool:
        """检查向量是否在屏幕外"""
        to_origin = v.clone().sub(self.origin)
        return (to_origin.x <= 0 or to_origin.y <= 0 or
                to_origin.x >= self.world_dimensions.x or to_origin.y >= self.world_dimensions.y)

    def get_streamlines_with_secondary_road(self) -> list[list[Vector]]:
        with_secondary = self.all_streamlines_simple[:]
        with_secondary.append(self.river_secondary_road)
        return with_secondary
