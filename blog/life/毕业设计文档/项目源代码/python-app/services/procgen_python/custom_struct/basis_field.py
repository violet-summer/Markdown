import math
from abc import ABC, abstractmethod

from .tensor import Tensor
from .vector import Vector


class FieldType:
    Radial = 0
    Grid = 1



class BasisField(ABC):
    def __init__(self, centre: Vector,size: float,decay: float):
        """
        初始化基础场
        :param 包含中心点、尺寸和衰减因子的参数
        """
        self._center = centre.clone()
        self._size = size
        self._decay = decay

    # 返回中心点坐标
    @property
    def center(self) -> Vector:
        return self._center.clone()

    # 设置中心点坐标
    @center.setter
    def center(self, centre: Vector):
        self._center.copy(centre)

    # 返回尺寸
    @property
    def size(self) -> float:
        return self._size
    # 设置尺寸
    @size.setter
    def size(self, size: float):
        self._size = size

    # 返回衰减因子，影响局部化
    @property
    def decay(self) -> float:
        return self._decay

    # 设置衰减因子
    @decay.setter
    def decay(self, decay: float):
        self._decay = decay

    # 抽象类，获取指定点的张量
    @abstractmethod
    def get_tensor(self, point: Vector) -> Tensor:
        """
        获取指定点的张量
        :param point: 点的坐标
        :return: Tensor 对象
        """
        pass

    def get_weighted_tensor(self, point: Vector, smooth: bool) -> Tensor:
        """
        获取加权张量
        :param point: 点的坐标
        :param smooth: 是否平滑处理
        :return: 加权后的 Tensor 对象
        """
        return self.get_tensor(point).scale(self._get_tensor_weight(point, smooth))

    # 主要逻辑
    # 先计算点到场中心的归一化距离 normDistanceToCentre，即距离除以场的 size。
    # 如果 smooth 为 true，权重为 normDistanceToCentre ** -decay，即距离越远，权重衰减越快（指数反比）。
    # 如果 smooth 为 false，则：
    # 若 decay 为 0 且点在 size 外，权重直接为 0（防止 0 次幂为 1 导致全屏有效）。
    # 否则权重为 (1 - normDistanceToCentre) ** decay，即在 size 范围内随距离线性衰减并指数调整，size 外为 0。
    # 注释解释
    # Interpolates between (0 and 1)^decay
    # 意思是：
    # 在 [0, 1] 区间内插值，并对结果做 decay 次幂。
    #
    # 当 decay > 1，衰减更快；
    # 当 decay < 1，衰减更慢；
    # decay = 0 时，理论上全为 1，但代码做了特殊处理，size 外为 0。
    # 项目中的意义
    # 这个权重函数决定了每个基础场（如一个格网或径向场）对空间中每个点的影响范围和强度分布。
    # 通过调整 decay 和 size，可以灵活控制场的影响力分布，实现不同的张量场组合效果。
    # 总结
    # 它是一个“带幂次插值的权重函数”，用于平滑或线性地控制基础场对张量场的贡献。
    def _get_tensor_weight(self, point: Vector, smooth: bool) -> float:
        """
        计算张量权重
        :param point: 点的坐标
        :param smooth: 是否平滑处理
        :return: 权重值
        """
        norm_distance_to_centre = point.clone().sub(self._center).length() / self._size
        if smooth:
            return norm_distance_to_centre ** -self._decay
        if self._decay == 0 and norm_distance_to_centre >= 1:
            return 0
        return max(0.0, (1.0 - norm_distance_to_centre)) ** self._decay



class Grid(BasisField):
    def __init__(self, centre: Vector,size: float,decay: float,theta: float,):
        """
        初始化网格场
        :param params: 包含中心点、尺寸、衰减因子和角度的参数结构体
        """
        super().__init__(centre,size,decay)
        self._theta = theta

    # 获取旋转角度
    @property
    def theta(self) -> float:
        return self._theta

    # 设置网格场的旋转角度
    @theta.setter
    def theta(self, theta: float):
        self._theta = theta

    # 获取网格场的张量，形式为 [cos(2*theta), sin(2*theta)]
    def get_tensor(self, point: Vector) -> Tensor:
        """
        获取指定点的张量
        :param point: 点的坐标
        :return: Tensor 对象
        """
        cos = math.cos(2 * self._theta)
        sin = math.sin(2 * self._theta)
        return Tensor(1, [cos, sin])


class Radial(BasisField):
    def __init__(self, centre: Vector,size: float,decay: float):
        """
        初始化径向场
        :param params: 包含中心点、尺寸和衰减因子的参数结构体
        """
        super().__init__(centre,size,decay)

    def get_tensor(self, point: Vector) -> Tensor:
        """
        获取指定点的张量
        :param point: 点的坐标
        :return: Tensor 对象
        """
        t = point.clone().sub(self._center)
        t1 = t.y**2 - t.x**2
        t2 = -2 * t.x * t.y
        return Tensor(1, [t1, t2])
