import math
from pathlib import Path

from opensimplex import OpenSimplex  # 使用SimplexNoise库
from tqdm import tqdm

from .polygon_util import PolygonUtil  # PolygonUtil已实现
from ..custom_struct import Vector, Tensor
from ..custom_struct.basis_field import BasisField, Radial, Grid
from ..custom_struct.util import Util


class NoiseParams:
    def __init__(self, global_noise, noise_size_park, noise_angle_park, noise_size_global, noise_angle_global):
        self.global_noise = global_noise
        self.noise_size_park = noise_size_park
        self.noise_angle_park = noise_angle_park  # 角度
        self.noise_size_global = noise_size_global
        self.noise_angle_global = noise_angle_global

class TensorField:

    def __init__(self, noise_params: NoiseParams, world_dimensions:Vector, origin=Vector(0, 0),zoom=0.5,smooth:bool=False,ignore_river=False):
        """
            初始化 TensorField 类的实例。

            参数:
                noise_params (NoiseParams): 噪声参数对象，包含以下属性：
                    - global_noise (bool): 是否启用全局噪声。
                    - noise_size_park (float): 公园噪声的大小参数。
                    - noise_angle_park (float): 公园噪声的角度参数（以度为单位）。
                    - noise_size_global (float): 全局噪声的大小参数。
                    - noise_angle_global (float): 全局噪声的角度参数（以度为单位）。

            功能:
                - 初始化张量场的基础属性，如噪声生成器、张量场范围、海洋和河流多边形等。
                - 设置默认的世界尺寸和原点。
        """
        # self.TENSOR_SPAWN_SCALE = 0.7
        # 含义：张量场（或基础张量网格）初始化时的缩放比例。
        # 用途：用于确定默认生成的基础张量网格（如 Grid、Radial）在整个世界范围中的占比。
        # 举例：如果世界尺寸是 2000×2000，TENSOR_SPAWN_SCALE = 0.7，则默认基础网格的尺寸为 1400×1400，通常居中放置。
        # 作用：让初始张量场不会铺满整个世界，而是留有边界，方便后续编辑和扩展。
        # self.TENSOR_LINE_DIAMETER = 20
        # 含义：张量可视化时，每个“十字”或“线段”的理想长度（像素单位）。
        # 用途：用于在画布上绘制张量主方向和副方向的线段时，控制每个张量“十字”的长度。
        # 作用：保证张量场可视化时，线段长度统一、清晰，便于观察主方向分布。
        if origin is None:
            origin = [0, 0]
        self.TENSOR_SPAWN_SCALE = 0.7
        self.TENSOR_LINE_DIAMETER = 20

        self.basis_fields:list[BasisField] = []  # 存储BasisField对象


        self.world_dimensions=world_dimensions
        self.parks:list[list[Vector]] = []  # 存储公园的多边形
        self.sea:list[Vector] = []  # 存储海洋的多边形
        self.river :list[Vector]= []  # 存储河流的多边形
        self.ignore_river = ignore_river  # 是否忽略河流

        self.smooth = smooth  # 是否平滑
        self.noise_params = noise_params
        self.origin = origin
        self.zoom=zoom

      

    def enable_global_noise(self, angle: float, size: float):
        """启用全局噪声"""
        self.noise_params.global_noise = True
        self.noise_params.noise_angle_global = angle
        self.noise_params.noise_size_global = size

    def disable_global_noise(self):
        """禁用全局噪声"""
        self.noise_params.global_noise = False

    def add_grid(self, centre: Vector, size: float, decay: float, theta: float):
        """添加网格场"""
        grid = Grid(centre, size, decay, theta)
        self.add_field(grid)

    def add_radial(self, centre: Vector, size: float, decay: float):
        """添加径向场"""
        radial = Radial(centre, size, decay)
        self.add_field(radial)

    def add_field(self, field: BasisField):
        """添加基础场"""
        self.basis_fields.append(field)

    def remove_field(self, field: BasisField):
        """移除基础场"""
        if field in self.basis_fields:
            self.basis_fields.remove(field)

    def reset(self):
        """重置所有数据"""
        self.basis_fields = []
        self.parks = []
        self.sea = []
        self.river = []

    def get_centre_points(self):
        """获取所有基础场的中心点"""
        return [field.center for field in self.basis_fields]

    def get_basis_fields(self):
        """获取所有基础场"""
        return self.basis_fields

    def sample_point(self, point: Vector) -> Tensor:
        """对某点进行采样"""
        if not self.on_land(point):
            # 如果不在陆地上，返回零张量
            return Tensor.zero()

        # 如果没有基础场，默认返回一个单位张量
        if not self.basis_fields:

            return Tensor(1, [0, 0])

        tensor_acc = Tensor.zero()
        for field in self.basis_fields:
            tensor_acc.add(field.get_weighted_tensor(point, self.smooth), self.smooth)

        # 如果点在公园内，添加旋转噪声
        if any(PolygonUtil.inside_polygon(point, park) for park in self.parks):
            tensor_acc.rotate(self.get_rotational_noise(point, self.noise_params.noise_size_park, self.noise_params.noise_angle_park))

        # 如果启用了全局噪声，添加全局旋转噪声 # print("启用了全局噪声，添加全局旋转噪声", self.noise_params.global_noise)
        if self.noise_params.global_noise:
            tensor_acc.rotate(self.get_rotational_noise(point, self.noise_params.noise_size_global, self.noise_params.noise_angle_global))

        return tensor_acc

    @staticmethod
    def get_rotational_noise(point: Vector, noise_size: float, noise_angle: float) -> float:
        """获取旋转噪声，噪声角度以度为单位"""

        noise = OpenSimplex(seed=42)
        return noise.noise2(point.x / noise_size, point.y / noise_size) * noise_angle * math.pi / 180

    def on_land(self, point: Vector) -> bool:
        """判断某点是否在陆地上"""
        in_sea = any(self.sea) and PolygonUtil.inside_polygon(point, self.sea)
        in_river = any(self.river) and PolygonUtil.inside_polygon(point, self.river)
        if self.ignore_river:
            return not in_sea

        return not in_sea and not in_river

    def in_parks(self, point: Vector) -> bool:
        """判断某点是否在公园内"""
        return any(PolygonUtil.inside_polygon(point, park) for park in self.parks)

    def set_recommended(self):
        """设置推荐的张量场"""
        self.reset()
        size = self.world_dimensions.multiply_scalar(self.TENSOR_SPAWN_SCALE)
        new_origin = self.world_dimensions \
            .multiply_scalar((1 - self.TENSOR_SPAWN_SCALE) / 2) \
            .add(self.origin)
        self.add_grid_at_location(new_origin)
        self.add_grid_at_location(new_origin.clone().add(size))
        self.add_grid_at_location(new_origin.clone().add(Vector(size.x, 0)))
        self.add_grid_at_location(new_origin.clone().add(Vector(0, size.y)))
        self.add_radial_random()

    def add_radial_random(self):
        """随机添加径向场"""
        width = self.world_dimensions.x
        self.add_radial(
            self.random_location(),
            Util.random_range(width / 10, width / 5),  # 尺寸
            Util.random_range(50)  # 衰减
        )

    def add_grid_random(self):
        """随机添加网格场"""
        self.add_grid_at_location(self.random_location())

    def add_grid_at_location(self, location: Vector):
        """在指定位置添加网格场"""
        width = self.world_dimensions.x
        self.add_grid(
            location,
            Util.random_range(width / 4, width),  # 尺寸
            Util.random_range(50),  # 衰减
            Util.random_range(math.pi / 2)  # 角度
        )

    def random_location(self) -> Vector:
        """生成张量场的随机位置"""
        size = self.world_dimensions.multiply_scalar(self.TENSOR_SPAWN_SCALE)
        location = Vector(Util.random_range(0, 1), Util.random_range(0, 1)).multiply(size)
        print("径向张量场的位置",location.x,location.y)
        new_origin = self.world_dimensions.multiply_scalar((1 - self.TENSOR_SPAWN_SCALE) / 2)

        return location.add(self.origin).add(new_origin)

    def visualize(self,dir=Path("./export/output/")):
        """
        获取用于张量场可视化的点的网格，并绘制张量场
        """
        import matplotlib.pyplot as plt
        import numpy as np

        # 增加一个密度因子来控制点的数量
        # 值 > 1 会增加点的密度。例如，2.0 会使点大约增加四倍。
        visualization_density_factor = 5.0  # 您可以调整此值以获得所需的点密度

        # 每个“十字”或“线段”的理想长度（经过缩放后的像素单位）
        # 通过除以密度因子来减小 diameter，从而增加点数
        # 这也会使得每个绘制的张量符号更小，以适应更密集的布局
        diameter = (self.TENSOR_LINE_DIAMETER / self.zoom) / visualization_density_factor
        
        world_dimensions = self.world_dimensions
        # 根据调整后的 diameter 重新计算网格点数
        n_hor = math.ceil(world_dimensions.x / diameter) + 1
        n_ver = math.ceil(world_dimensions.y / diameter) + 1
        origin_x = diameter * math.floor(self.origin.x / diameter)
        origin_y = diameter * math.floor(self.origin.y / diameter)

        # 使用 NumPy 加速点生成
        x_coords = np.linspace(origin_x, origin_x + n_hor * diameter, n_hor + 1)
        y_coords = np.linspace(origin_y, origin_y + n_ver * diameter, n_ver + 1)
        xv, yv = np.meshgrid(x_coords, y_coords)
        x_flat = xv.flatten()
        y_flat = yv.flatten()

        # 使用 tqdm 显示进度条
        points = []
        tensors = []
        for x, y in tqdm(zip(x_flat, y_flat), total=len(x_flat), desc="Processing Points for Visualization"):
            point = Vector(x, y)
            points.append(point)
            tensors.append(self.sample_point(point))  # 采样张量

        # 可视化张量场
        plt.figure(figsize=(160, 90)) # 可以适当调整图像大小以容纳更多点
        for point, tensor in zip(points, tensors):
            if tensor.r == 0:
                continue  # 跳过零张量

            # 获取主方向向量
            major = tensor.get_major()
            # 绘制的线段长度也基于调整后的 diameter
            dx_major = major.x * tensor.r * diameter * 0.2
            dy_major = major.y * tensor.r * diameter * 0.2

            # 获取次方向向量
            minor = tensor.get_minor()
            dx_minor = minor.x * tensor.r * diameter * 0.2
            dy_minor = minor.y * tensor.r * diameter * 0.2

            # 绘制张量的主方向和次方向为交叉十字
            plt.plot(
                [point.x - dx_major, point.x + dx_major],
                [point.y - dy_major, point.y + dy_major],
                color='blue', alpha=1, linewidth=4 # 可以调整线条宽度
            )
            plt.plot(
                [point.x - dx_minor, point.x + dx_minor],
                [point.y - dy_minor, point.y + dy_minor],
                color='red', alpha=1, linewidth=4# 可以调整线条宽度
            )
        xlim = plt.xlim()
        plt.xlim(xlim[1], xlim[0])
        plt.title("Tensor Field Visualization (Higher Density)")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(True, linestyle='--', alpha=1)
        plt.axis("equal")
        plt.tight_layout()
        # 确保输出目录存在
        output_dir = dir
        output_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_dir.joinpath("tensor_visualization.svg"), bbox_inches='tight', pad_inches=0.05, dpi=100) # 可以调整 DPI
        # plt.show() # 如果需要立即显示，取消此行注释
