import math
from .vector import Vector  # 假设 vector.py 文件中定义了 Vector 类

class Tensor:

    # 对称二维张量，而且只关心“主方向”和“强度”，因此只有两个元素
    def __init__(self, r: float, matrix: list[float]):
        """
        初始化 Tensor 对象
        :param r: 模长
        :param matrix: 矩阵，表示为一个包含两个元素的列表
        """
        self.r = r
        self.matrix = matrix  # 比如:矩阵表示为 [0, 1] 和 [1, -0]
        self.old_theta = False  # 标记 theta 是否需要重新计算
        self._theta = self._calculate_theta()  # 初始化 theta
    # 构建张量的逻辑直接写在了field实现中，这里的实现是废弃的
    # @staticmethod
    # def from_angle(angle: float) -> 'Tensor':
    #     """
    #     根据角度创建 Tensor 对象
    #     :param angle: 角度（弧度制）
    #     :return: Tensor 对象
    #     """
    #     return Tensor(1, [math.cos(angle * 4), math.sin(angle * 4)])

    # @staticmethod
    # def from_vector(vector: Vector) -> 'Tensor':
    #     """
    #     根据向量创建 Tensor 对象
    #     :param vector: Vector 对象
    #     :return: Tensor 对象
    #     """
    #     t1 = vector.x ** 2 - vector.y ** 2
    #     t2 = 2 * vector.x * vector.y
    #     t3 = t1 ** 2 - t2 ** 2
    #     t4 = 2 * t1 * t2
    #     return Tensor(1, [t3, t4])

    @staticmethod
    def zero() -> 'Tensor':
        """
        返回零张量
        :return: Tensor 对象
        """
        return Tensor(0, [0, 0])

    @property
    def theta(self) -> float:
        """
        获取当前的 theta 值
        :return: theta 值
        """
        if self.old_theta:
            self._theta = self._calculate_theta()
            self.old_theta = False
        return self._theta

    def add(self, tensor: 'Tensor', smooth: bool) -> 'Tensor':
        """
        将另一个张量加到当前张量
        :param tensor: 另一个 Tensor 对象
        :param smooth: 是否平滑处理
        :return: 当前 Tensor 对象
        """
        # 两个张量的第一个第二个值乘以r然后相加
        self.matrix = [v * self.r + tensor.matrix[i] * tensor.r for i, v in enumerate(self.matrix)]

        if smooth:
            # hypot:sqrt(x**2 + y**2)。
            self.r = math.hypot(*self.matrix)
            self.matrix = [v / self.r for v in self.matrix]
        else:
            self.r = 2

        self.old_theta = True
        return self

    def scale(self, s: float) -> 'Tensor':
        """
        缩放张量
        :param s: 缩放因子
        :return: 当前 Tensor 对象
        """
        self.r *= s
        self.old_theta = True
        return self

    def rotate(self, theta: float) -> 'Tensor':
        """
        旋转张量
        :param theta: 旋转角度（弧度制）
        :return: 当前 Tensor 对象
        """
        if theta == 0:
            return self

        new_theta = self.theta + theta
        if new_theta < math.pi:
            new_theta += math.pi
        if new_theta >= math.pi:
            new_theta -= math.pi

        self.matrix[0] = math.cos(2 * new_theta) * self.r
        self.matrix[1] = math.sin(2 * new_theta) * self.r
        self._theta = new_theta
        return self

    def get_major(self) -> Vector:
        """
        获取主方向向量
        :return: Vector 对象
        """
        if self.r == 0:  # 退化情况
            return Vector.zero_vector()
        return Vector(math.cos(self.theta), math.sin(self.theta))

    def get_minor(self) -> Vector:
        """
        获取次方向向量
        :return: Vector 对象
        """
        if self.r == 0:  # 退化情况
            return Vector.zero_vector()
        angle = self.theta + math.pi / 2
        return Vector(math.cos(angle), math.sin(angle))

    def _calculate_theta(self) -> float:
        """
        计算 theta 值
        :return: theta 值
        """
        if self.r == 0:
            return 0
            # atan2反正切符号，求正切角度，提供y/x即可，自动识别正负号返回正确的角度，避免角度歧义
        return math.atan2(self.matrix[1] / self.r, self.matrix[0] / self.r) / 2
