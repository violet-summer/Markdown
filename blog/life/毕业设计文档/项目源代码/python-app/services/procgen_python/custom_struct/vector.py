import math
import logging

class Vector:
    """
    一个二维向量类，提供多种向量操作的实用方法。
    """

    def __init__(self, x: float, y: float):
        """
        初始化一个二维向量，包含x和y分量。
        :param x: 向量的x分量。
        :param y: 向量的y分量。
        """
        self.x = x
        self.y = y

    def to_dict(self):
        return {"x": self.x, "y": self.y}
    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"])
    @staticmethod
    def zero_vector() -> 'Vector':
        """
        创建一个零向量 (0, 0)。
        :return: 一个新的零向量实例。
        """
        return Vector(0, 0)

    @staticmethod
    def from_scalar(s: float) -> 'Vector':
        """
        创建一个分量值相同的向量。
        :param s: 标量值。
        :return: 一个新的向量实例，x和y分量均为s。
        """
        return Vector(s, s)

    @staticmethod
    def angle_between(v1: 'Vector', v2: 'Vector') -> float:
        """
        计算两个向量之间的夹角（弧度制）。
        :param v1: 第一个向量。
        :param v2: 第二个向量。
        :return: 两个向量之间的夹角，范围为[-pi, pi]。
        """
        angle_between = v1.angle() - v2.angle()
        if angle_between > math.pi:
            angle_between -= 2 * math.pi
        elif angle_between <= -math.pi:
            angle_between += 2 * math.pi
        return angle_between

    @staticmethod
    def is_left(line_point: 'Vector', line_direction: 'Vector', point: 'Vector') -> bool:
        """
        判断一个点是否位于一条有向直线的左侧。
        :param line_point: 直线上的一点。
        :param line_direction: 直线的方向向量。
        :param point: 要测试的点。
        :return: 如果点在直线左侧返回True，否则返回False。
        """
        perpendicular_vector = Vector(line_direction.y, -line_direction.x)
        return point.clone().sub(line_point).dot(perpendicular_vector) < 0

    def add(self, v: 'Vector') -> 'Vector':
        """
        将另一个向量加到当前向量上。
        :param v: 要相加的向量。
        :return: 更新后的向量。
        """
        self.x += v.x
        self.y += v.y
        return self

    def sub(self, v: 'Vector') -> 'Vector':
        """
        从当前向量中减去另一个向量。
        :param v: 要减去的向量。
        :return: 更新后的向量。
        """
        self.x -= v.x
        self.y -= v.y
        return self

    def multiply_scalar(self, scalar: float) -> 'Vector':
        """
        将当前向量乘以一个标量。
        :param scalar: 标量值。
        :return: 更新后的向量。
        """
        self.x *= scalar
        self.y *= scalar
        return self

    def length(self) -> float:
        """
        计算向量的长度（模）。
        :return: 向量的长度。
        """
        return math.sqrt(self.length_sq())

    def length_sq(self) -> float:
        """
        计算向量长度的平方。
        :return: 向量长度的平方。
        """
        return self.x * self.x + self.y * self.y

    def normalize(self) -> 'Vector':
        """
        将向量归一化，使其长度为1。
        :return: 归一化后的向量。
        """
        l = self.length()
        if l == 0:
            logging.warning("Zero Vector")
            return self
        return self.divide_scalar(l)

    def clone(self) -> 'Vector':
        """
        创建当前向量的副本。
        :return: 一个新的向量实例，分量与当前向量相同。
        """
        return Vector(self.x, self.y)

    def copy(self, v: 'Vector') -> 'Vector':
        """
        将另一个向量的分量复制到当前向量。
        :param v: 要复制的向量。
        :return: 更新后的向量。
        """
        self.x = v.x
        self.y = v.y
        return self

    def cross(self, v: 'Vector') -> float:
        """
        计算当前向量与另一个向量的叉积。
        :param v: 另一个向量。
        :return: 叉积的标量值。
        """
        return self.x * v.y - self.y * v.x

    def distance_to(self, v: 'Vector') -> float:
        """
        计算当前向量到另一个向量的距离。
        :param v: 另一个向量。
        :return: 两个向量之间的距离。
        """
        return math.sqrt(self.distance_to_squared(v))

    def distance_to_squared(self, v: 'Vector') -> float:
        """
        计算当前向量到另一个向量的距离的平方。
        :param v: 另一个向量。
        :return: 两个向量之间距离的平方。
        """
        dx = self.x - v.x
        dy = self.y - v.y
        return dx * dx + dy * dy

    def divide(self, v: 'Vector') -> 'Vector':
        """
        当前向量按分量除以另一个向量。
        :param v: 要除以的向量。
        :return: 更新后的向量。
        """
        if v.x == 0 or v.y == 0:
            logging.warning("Division by zero")
            return self
        self.x /= v.x
        self.y /= v.y
        return self

    def divide_scalar(self, s: float) -> 'Vector':
        """
        当前向量按标量值进行除法。
        :param s: 标量值。
        :return: 更新后的向量。
        """
        if s == 0:
            logging.warning("Division by zero")
            return self
        return self.multiply_scalar(1 / s)

    def dot(self, v: 'Vector') -> float:
        """
        计算当前向量与另一个向量的点积。
        :param v: 另一个向量。
        :return: 点积的标量值。
        """
        return self.x * v.x + self.y * v.y

    def equals(self, v: 'Vector') -> bool:
        """
        检查当前向量是否与另一个向量相等。
        :param v: 另一个向量。
        :return: 如果两个向量相等返回True，否则返回False。
        """
        return self.x == v.x and self.y == v.y

    def multiply(self, v: 'Vector') -> 'Vector':
        """
        当前向量按分量与另一个向量相乘。
        :param v: 要相乘的向量。
        :return: 更新后的向量。
        """
        self.x *= v.x
        self.y *= v.y
        return self

    def negate(self) -> 'Vector':
        """
        取当前向量的相反向量（方向相反）。
        :return: 更新后的向量。
        """
        return self.multiply_scalar(-1)

    def rotate_around(self, center: 'Vector', angle: float) -> 'Vector':
        """
        将当前向量绕指定中心点旋转指定角度。
        :param center: 旋转中心点。
        :param angle: 旋转角度（弧度制）。
        :return: 更新后的向量。
        """
        cos = math.cos(angle)
        sin = math.sin(angle)

        x = self.x - center.x
        y = self.y - center.y

        self.x = x * cos - y * sin + center.x
        self.y = x * sin + y * cos + center.y
        return self

    def set(self, v: 'Vector') -> 'Vector':
        """
        将当前向量的分量设置为另一个向量的分量。
        :param v: 要复制的向量。
        :return: 更新后的向量。
        """
        self.x = v.x
        self.y = v.y
        return self

    def set_x(self, x: float) -> 'Vector':
        """
        设置当前向量的x分量。
        :param x: 新的x值。
        :return: 更新后的向量。
        """
        self.x = x
        return self

    def set_y(self, y: float) -> 'Vector':
        """
        设置当前向量的y分量。
        :param y: 新的y值。
        :return: 更新后的向量。
        """
        self.y = y
        return self

    def set_length(self, length: float) -> 'Vector':
        """
        设置当前向量的长度，同时保持方向不变。
        :param length: 新的长度。
        :return: 更新后的向量。
        """
        return self.normalize().multiply_scalar(length)

    def angle(self) -> float:
        """
        计算当前向量相对于正x轴的角度。
        :return: 角度值，范围为[-pi, pi]。
        """
        return math.atan2(self.y, self.x)

    def __repr__(self) -> str:
        """
        返回向量的字符串表示形式。
        :return: 字符串格式 "Vector(x, y)"。
        """
        return f"Vector({self.x}, {self.y})"
