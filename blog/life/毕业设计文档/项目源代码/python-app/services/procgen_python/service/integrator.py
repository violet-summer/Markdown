from abc import ABC, abstractmethod

from app.services.procgen_python.custom_struct import Vector
from app.services.procgen_python.custom_struct.streamline_interface import StreamlineParams
from .tensor_field import TensorField



class FieldIntegrator(ABC):
    """张量场积分器抽象基类"""

    def __init__(self, field: TensorField):
        """
        初始化场积分器

        参数:
            field: 张量场对象
        """
        self.field = field

    @abstractmethod
    def integrate(self, point: Vector, major: bool) -> Vector:
        """
        积分方法（抽象方法，需要子类实现）

        参数:
            point: 积分起点
            major: 是否使用主方向

        返回:
            积分结果向量
        """
        pass

    def sample_field_vector(self, point: Vector, major: bool) -> Vector:
        """
        ��指定点采样场向量

        参数:
            point: 采样点
            major: 是否采样主方向

        返回:
            采样得到的向量
        """
        # print("采样得到的向量")
        tensor = self.field.sample_point(point)
        if major:
            # print("采样得到的major向量")
            return tensor.get_major()
        return tensor.get_minor()

    def on_land(self, point: Vector) -> bool:
        """
        检查点是否在陆地上

        参数:
            point: 检查点

        返回:
            是否在陆地上
        """
        return self.field.on_land(point)


class EulerIntegrator(FieldIntegrator):
    """欧拉积分器实现类"""

    def __init__(self, field: TensorField, params:StreamlineParams):
        """
        初始化欧拉积分器

        参数:
            field: 张量场对象
            params: 流线参数，包含步长dstep
        """
        super().__init__(field)
        self.params = params

    def integrate(self, point: Vector, major: bool) -> Vector:
        """
        使用欧拉方法进行积分

        参数:
            point: 积分起点
            major: 是否使用主方向

        返回:
            积分结果向量
        """
        return self.sample_field_vector(point, major).multiply_scalar(self.params.dstep)


class RK4Integrator(FieldIntegrator):
    """四阶龙格-库塔积分器实现类"""

    def __init__(self, field: TensorField, params:StreamlineParams):
        """
        初始化四阶龙格-库塔积分器

        参数:
            field: 张量场对象
            params: 流线参数，包含步长dstep
        """
        super().__init__(field)
        self.params = params

    def integrate(self, point: Vector, major: bool) -> Vector:
        """
        使用四阶龙格-库塔方法进行积分

        参数:
            point: 积分起点
            major: 是否使用主方向

        返回:
            积分结果向量
        """
        # 计算RK4方法的四个关键点
        k1 = self.sample_field_vector(point, major)
        k23 = self.sample_field_vector(point.clone().add(Vector.from_scalar(self.params.dstep / 2)), major)
        k4 = self.sample_field_vector(point.clone().add(Vector.from_scalar(self.params.dstep)), major)
        # print("rk4 integrate k1",k1)
        # 组合结果
        return k1.add(k23.multiply_scalar(4)).add(k4).multiply_scalar(self.params.dstep / 6)
