from typing import List, Callable, Optional

from trimesh import Trimesh

from app.services.procgen_python.service.graph import Graph
from app.services.procgen_python.service.polygon_finder import PolygonFinder
from app.services.procgen_python.service.polygon_util import PolygonUtil
from app.services.procgen_python.service.tensor_field import TensorField
from app.services.procgen_python.custom_struct import Vector, PolygonParams
from app.services.procgen_python.custom_struct.params import MapBuildingsParams


class BuildingModel:
    """
    Represents a 3D building model
    """
    def __init__(self, lot_world: List[Vector]):
        """
        Initialize a building model
        
        Args:
            lot_world: The building lot in world space
        """
        self.height = 20 + 20 * (hash(str(lot_world)) % 100) / 100  # Deterministic random height
        self.lot_world = lot_world
        self.lot_screen = []
        self.roof = []
        self.sides = []


class BuildingModels:
    """
    Represents a collection of 3D building models
    """

    def __init__(self, lots: List[List[Vector]]):
    
        self._building_models = []

        for lot in lots:
            self._building_models.append({
                "height": 20 + 20 * (hash(str(lot)) % 100) / 100,  # Deterministic random height
                "lot_world": lot,
                "lot_screen": [],
                "roof": [],
                "sides": []
            })

        self._building_models.sort(key=lambda b: b["height"])

    @property
    def building_models(self) -> List[dict]:
        """
        Get the building models

        Returns:
            List of building models
        """
        return self._building_models

    @staticmethod
    def _get_building_sides( b: dict) -> List[List[Vector]]:
        """
        Get sides of buildings by joining corresponding edges between the roof and ground

        Args:
            b: The building model

        Returns:
            List of polygons representing the sides
        """
        polygons = []
        for i in range(len(b["lot_screen"])):
            next_i = (i + 1) % len(b["lot_screen"])
            polygons.append([b["lot_screen"][i], b["lot_screen"][next_i], b["roof"][next_i], b["roof"][i]])
        return polygons

class Buildings:
    """
    Finds building lots and creates 3D buildings
    """
    def __init__(self, tensor_field: TensorField, dstep: float, all_streamlines:list[list[Vector]],building_params: MapBuildingsParams= MapBuildingsParams(
            max_length=20,
            min_area=50,
            shrink_spacing=4,
            chance_no_divide=5
        ),animate: bool = False,):
        """
        Initialize the Buildings class
        
        Args:
            tensor_field: The tensor field
            dstep: The step size for the graph
            animate: Whether to animate the generation
        """
        self.g = None
        self.tensor_field = tensor_field
        self.dstep = dstep
        self._animate = animate
        self.all_streamlines = all_streamlines
        # self.pre_generate_callback: Callable[[], None] = lambda: None
        # self.post_generate_callback: Callable[[], None] = lambda: None
        
        self.building_params = building_params
        
        self.polygon_finder = PolygonFinder([], self.building_params, self.tensor_field)
        self._models:BuildingModels = BuildingModels([])
    
    @property
    def lots(self) -> List[List[Vector]]:
        """
        Get the building lots in screen space
        
        Returns:
            The building lots
        """
        return self.polygon_finder.polygons
    
    @property
    def models(self) -> List[BuildingModel]:
        """
        Get the building models
        
        Returns:
            The building models
        """
        return self._models
    
    def set_all_streamlines(self, streamlines: List[List[Vector]]) -> None:
        """
        Set all streamlines
        
        Args:
            streamlines: The streamlines
        """
        self.all_streamlines = streamlines
    
    def reset(self) -> None:
        """
        Reset the buildings
        """
        self.polygon_finder.reset()
        self._models = []
    
    def update(self) -> bool:
        """
        Update the buildings
        
        Returns:
            True if the buildings were updated, False otherwise
        """
        return self.polygon_finder.update()
    
    def generate(self) -> None:
        """
        Generate buildings
        
        Args:

        """
        # self.pre_generate_callback()
        self._models = []
        
        # # Create a graph from all streamlines
        # g = Graph(self.all_streamlines, self.dstep, True)
        #
        # Find polygons
        self.polygon_finder = PolygonFinder(self.g.nodes, self.building_params, self.tensor_field)
        self.polygon_finder.find_polygons()
        

        # 递归切分
        self.polygon_finder.shrink()
        self.polygon_finder.divide()
        
        # Create building models
        self._models = [BuildingModel(polygon) for polygon in self.polygon_finder.polygons]
        mesh=Trimesh()
        # 直接生成模型
        for model in self.polygon_finder._divided_polygons:
            mesh+=PolygonUtil.polygon_to_shape_to_mesh(model,2)
            
            # self._models.append(BuildingModel(model))
        mesh.export("./export/output/buildings_divided.obj")

    def get_blocks(self) -> List[List[Vector]]:
        """
        获取建筑块的多边形列表

        Returns:
            List[List[Vector]]: 转换为屏幕空间的多边形列表
        """
        if not self.all_streamlines:
            print("日志: all_streamlines 为空，无法生成建筑块")
            return []
        print("Graph")
        self.g = Graph(self.all_streamlines, self.dstep, True)
        print("Graph完成")
        # todo 这里待修改,查找多边形的参数不能和控制建筑块的参数相同，公园、建筑、地块分属三种不同的参数比较好
        block_params = self.building_params.copy()
        block_params.shrink_spacing = block_params.shrink_spacing / 2
        self.polygon_finder = PolygonFinder(self.g.nodes, block_params, self.tensor_field)
        self.polygon_finder.find_polygons()
        self.polygon_finder.shrink(False)
        self.polygon_finder.divide()
        
        # Create building models
        # self._models = [BuildingModel(polygon) for polygon in self.polygon_finder.polygons]
        
        # 不需要从世界坐标系到屏幕坐标系的转化
        return self.polygon_finder.get_shrunk_polygons()