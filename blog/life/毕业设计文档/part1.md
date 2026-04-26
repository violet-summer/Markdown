## 第三章 核心模块实现

### 张量场模块 (`tensor.py`)

`tensor.py` 定义了 `Tensor` 类，封装二维对称张量的基本运算。

```python
class Tensor:
    def __init__(self, a, b):
        self.matrix = [a, b]  # 存储 [a, b] 对应矩阵 [[a, b], [b, -a]]
        self._theta = None

    @staticmethod
    def from_angle(theta, r=1.0):
        """从角度和模长创建张量"""
        a = r * math.cos(2 * theta)
        b = r * math.sin(2 * theta)
        return Tensor(a, b)

    def get_major(self):
        """返回主方向单位向量 (cosθ, sinθ)"""
        if self._theta is None:
            self._theta = 0.5 * math.atan2(self.matrix[1], self.matrix[0])
        return (math.cos(self._theta), math.sin(self._theta))

    def add(self, other):
        """张量叠加"""
        return Tensor(self.matrix[0] + other.matrix[0],
                      self.matrix[1] + other.matrix[1])

    def rotate(self, angle):
        """旋转张量（即主方向增加 angle/2？注意：旋转张量等价于主方向增加 angle/2？）
        实际上，旋转张量矩阵 R(θ) T R(-θ) 对应主方向增加 θ，但我们的参数化已经隐含。
        简便起见，直接修改角度。
        """
        # 更简单的实现：从当前角度旋转
        cur_theta = self.get_theta()
        new_theta = cur_theta + angle
        return Tensor.from_angle(new_theta, self.get_magnitude())
```

### 基础场模块 (`basis_field.py`)

定义抽象基类 `BasisField`，子类实现具体的张量计算。

```python
class BasisField(ABC):
    def __init__(self, center, size, decay):
        self.center = np.array(center)
        self.size = size
        self.decay = decay

    def get_weight(self, p):
        d2 = np.sum((p - self.center) ** 2)
        return np.exp(-d2 / (self.decay * self.size ** 2))

    @abstractmethod
    def get_tensor(self, p):
        pass

    def get_weighted_tensor(self, p):
        w = self.get_weight(p)
        if w < 1e-6:
            return Tensor.zero()
        T = self.get_tensor(p)
        return T.scale(w)
```

`Grid` 类实现网格场：

```python
class Grid(BasisField):
    def __init__(self, center, size, decay, theta):
        super().__init__(center, size, decay)
        self.theta = theta

    def get_tensor(self, p):
        return Tensor.from_angle(self.theta)
```

`Radial` 类实现径向场：

```python
class Radial(BasisField):
    def get_tensor(self, p):
        v = p - self.center
        d2 = np.sum(v ** 2)
        if d2 < 1e-6:
            return Tensor.zero()
        x, y = v
        # 矩阵元素：a = (y^2 - x^2) / d2, b = -2xy / d2
        a = (y*y - x*x) / d2
        b = -2 * x * y / d2
        return Tensor(a, b)
```

### 流线生成模块 (`streamlines.py`)

`StreamlineGenerator` 类负责流线积分。

```python
class StreamlineGenerator:
    def __init__(self, tensor_field, grid_storage, params):
        self.tensor_field = tensor_field
        self.grid = grid_storage
        self.params = params

    def integrate_streamline(self, seed_point, direction=1):
        """从种子点沿 direction (+1 或 -1) 积分流线"""
        points = [seed_point]
        p = seed_point
        for _ in range(self.params.path_iterations):
            v = self.tensor_field.get_major(p)
            v = v * direction
            # RK2 step
            k1 = v * self.params.dstep
            mid = p + 0.5 * k1
            v_mid = self.tensor_field.get_major(mid)
            k2 = v_mid * self.params.dstep
            p_next = p + k2
            # 碰撞检测
            if not self.grid.is_valid_sample(p_next, self.params.dtest):
                break
            if self.out_of_bounds(p_next):
                break
            points.append(p_next)
            p = p_next
        return points
```

简化函数使用道格拉斯-普克算法：

```python
def simplify_streamline(points, tolerance):
    if len(points) < 3:
        return points
    start, end = points[0], points[-1]
    # 找到最远点
    dmax = 0
    index = 0
    for i in range(1, len(points)-1):
        d = point_line_distance(points[i], start, end)
        if d > dmax:
            dmax = d
            index = i
    if dmax > tolerance:
        # 递归
        left = simplify_streamline(points[:index+1], tolerance)
        right = simplify_streamline(points[index:], tolerance)
        return left[:-1] + right
    else:
        return [start, end]
```

### 空间索引模块 (`grid_storage.py`)

`GridStorage` 实现网格索引：

```python
class GridStorage:
    def __init__(self, world_dimensions, dsep):
        self.cell_size = dsep
        self.width = world_dimensions[0]
        self.height = world_dimensions[1]
        self.nx = int(math.ceil(self.width / self.cell_size)) + 1
        self.ny = int(math.ceil(self.height / self.cell_size)) + 1
        self.grid = [[[] for _ in range(self.ny)] for _ in range(self.nx)]

    def _grid_coords(self, p):
        ix = int(math.floor(p[0] / self.cell_size))
        iy = int(math.floor(p[1] / self.cell_size))
        return ix, iy

    def add_sample(self, p):
        ix, iy = self._grid_coords(p)
        if 0 <= ix < self.nx and 0 <= iy < self.ny:
            self.grid[ix][iy].append(p)

    def get_nearby_points(self, p, radius):
        ix, iy = self._grid_coords(p)
        radius_cells = int(math.ceil(radius / self.cell_size))
        points = []
        for i in range(ix - radius_cells, ix + radius_cells + 1):
            for j in range(iy - radius_cells, iy + radius_cells + 1):
                if 0 <= i < self.nx and 0 <= j < self.ny:
                    points.extend(self.grid[i][j])
        return points
```

### 图构建模块 (`graph.py`)

`Graph` 类管理节点和边，使用R树加速相交检测。

```python
from rtree import index

class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []
        self.rtree = index.Index()

    def add_segment(self, seg):
        self.segments.append(seg)
        # 插入包围盒到R树
        self.rtree.insert(len(self.segments)-1, seg.bbox)

    def find_intersections(self):
        intersections = []
        for i, seg in enumerate(self.segments):
            # 查询可能相交的线段
            candidates = list(self.rtree.intersection(seg.bbox))
            for j in candidates:
                if j <= i:
                    continue
                other = self.segments[j]
                if seg.intersects(other):
                    pt = seg.intersection_point(other)
                    if pt:
                        intersections.append(pt)
        return intersections
```

### 多边形查找模块 (`polygon_finder.py`)

`PolygonFinder` 实现右手法则遍历。

```python
class PolygonFinder:
    def __init__(self, graph):
        self.graph = graph
        self.visited_edges = set()

    def find_polygons(self):
        polygons = []
        for node in self.graph.nodes:
            for neighbor in node.neighbors:
                edge = (node, neighbor)
                if edge in self.visited_edges:
                    continue
                poly = self.walk_polygon(node, neighbor)
                if poly:
                    polygons.append(poly)
        return polygons

    def walk_polygon(self, start_node, first_neighbor):
        poly = [start_node.pos]
        curr = first_neighbor
        prev = start_node
        while True:
            poly.append(curr.pos)
            # 标记当前边为已访问
            self.visited_edges.add((prev, curr))
            # 找最靠右的下一个节点
            next_node = self.get_rightmost_node(prev, curr)
            if next_node is None:
                return None  # 死路
            if next_node == start_node:
                # 闭合
                break
            prev, curr = curr, next_node
        return poly
```

### 几何工具模块 (`polygon_util.py`)

提供面积计算、点在多边形内测试等函数。

```python
class PolygonUtil:
    @staticmethod
    def area(poly):
        """鞋带公式"""
        s = 0
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i+1)%n]
            s += x1*y2 - x2*y1
        return abs(s) / 2

    @staticmethod
    def point_in_polygon(p, poly):
        """射线法"""
        x, y = p
        inside = False
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i+1)%n]
            if ((y1 > y) != (y2 > y)) and (x < (x2-x1)*(y-y1)/(y2-y1) + x1):
                inside = not inside
        return inside
```

### 建筑生成模块 (`buildings.py`)

`Buildings` 类集成多边形查找和处理。

```python
class Buildings:
    def __init__(self, graph, tensor_field, params):
        self.graph = graph
        self.tensor_field = tensor_field
        self.params = params
        self.finder = PolygonFinder(graph)
        self.lots = []

    def generate(self, water_polygons):
        # 找到所有规划地块
        raw_polygons = self.finder.find_polygons()
        # 过滤水域
        land_polygons = self.filter_water(raw_polygons, water_polygons)
        for poly in land_polygons:
            # 收缩
            shrunk = self.shrink(poly, self.params.shrink_spacing)
            if shrunk is None:
                continue
            # 递归分割
            divided = self.divide(shrunk)
            self.lots.extend(divided)
```

### 水体生成模块 (`water_generator.py`)

`WaterGenerator` 类使用带噪声的流线生成水体。

```python
class WaterGenerator:
    def __init__(self, tensor_field, grid_storage, params):
        self.tensor_field = tensor_field
        self.grid = grid_storage
        self.params = params

    def create_coast(self):
        streamlines = []
        for seed in self.generate_seeds():
            # 生成带噪声的流线
            streamline = self.integrate_noisy(seed, self.params.coastline)
            if streamline:
                # 扩展至边界
                streamline = self.extend_to_boundary(streamline)
                # 细分
                streamline = self.complexify(streamline)
                streamlines.append(streamline)
        # 组合成海洋多边形
        sea = self.build_sea_polygon(streamlines)
        return sea
```

### 参数配置模块 (`params.py`)

使用Pydantic定义参数模型。

```python
from pydantic import BaseModel, validator
from typing import List, Optional

class GridFieldParams(BaseModel):
    x: float
    y: float
    size: float
    decay: float
    theta: float

class TensorFieldParams(BaseModel):
    smooth: bool = True
    grids: List[GridFieldParams] = []
    radials: List[RadialFieldParams] = []

class StreamlineDevParams(BaseModel):
    path_iterations: int = 1000
    seed_tries: int = 100
    dstep: float = 1.0
    dlookahead: float = 10.0
    dcirclejoin: float = 1.0
    joinangle: float = 0.1
    simplify_tolerance: float = 0.05
    collide_early: bool = False

class RoadLevelParams(BaseModel):
    dsep: float
    dtest: float
    dev_params: StreamlineDevParams

class ALLParams(BaseModel):
    world_dimensions: List[float] = [400, 400]
    origin: List[float] = [0, 0]
    tensor_field: TensorFieldParams
    water: WaterParams
    main: RoadLevelParams
    major: RoadLevelParams
    minor: RoadLevelParams
    parks: ParkParams
    buildings: BuildingParams
    park_polygons: PolygonParams

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            data = json.load(f)
        return cls(**data)
```