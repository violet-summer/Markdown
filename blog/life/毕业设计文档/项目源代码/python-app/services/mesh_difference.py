
import os
from pathlib import Path

import trimesh
# 直接指定 Blender 路径，无需环境变量
blender_dir = r"C:\APP\Blender Foundation\Blender 4.4"
blender_exe = r"C:\APP\Blender Foundation\Blender 4.4\blender.exe"
trimesh.boolean.BLENDER_PATH = blender_exe
# 自动将 Blender 目录加入 PATH，避免 'blender' is not in PATH 错误
os.environ["PATH"] = blender_dir + ";" + os.environ.get("PATH", "")

import trimesh
# 直接指定 Blender 路径，无需环境变量
trimesh.boolean.BLENDER_PATH = r"C:\APP\Blender Foundation\Blender 4.4\blender.exe"

import logging
from typing import Optional

import manifold3d as m3d
import numpy as np
from trimesh import Trimesh


def ensure_mesh(trimesh_obj):
    """将 trimesh.Scene 合并为单个网格，否则直接返回"""
    if isinstance(trimesh_obj, trimesh.Scene):
        # 合并场景中的所有几何体
        return trimesh.util.concatenate(trimesh_obj.dump())
    return trimesh_obj

def save_mesh_copy(trimesh_obj, output_path):
    """将 trimesh 对象导出到指定路径（自动根据扩展名判断格式）"""
    trimesh_obj.export(output_path)

def load_and_convert_to_manifold(file_path):
    """加载文件并转换为 manifold3d.Manifold 对象"""
    mesh_trimesh = trimesh.load(file_path)
    mesh_trimesh = ensure_mesh(mesh_trimesh)

    verts = mesh_trimesh.vertices.astype(np.float32)
    faces = mesh_trimesh.faces.astype(np.uint32)

    mesh = m3d.Mesh(vert_properties=verts, tri_verts=faces)
    manifold = m3d.Manifold(mesh)
    return manifold, mesh_trimesh

def manifold_to_trimesh(manifold_obj):
    """将 manifold3d.Manifold 转换为 trimesh.Trimesh"""
    mesh = manifold_obj.to_mesh()
    verts = mesh.vert_properties
    faces = mesh.tri_verts
    return trimesh.Trimesh(vertices=verts, faces=faces)

def difference_two(main_path, other_path, output_dir):
    """
    计算 main - other 的差集，并将原始模型和结果保存到 output_dir。
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载模型
    main_manifold, main_trimesh = load_and_convert_to_manifold(main_path)
    other_manifold, other_trimesh = load_and_convert_to_manifold(other_path)

    # 保存原始模型副本
    main_name = Path(main_path).stem + "_original.glb"
    other_name = Path(other_path).stem + "_original.glb"
    save_mesh_copy(main_trimesh, output_dir / main_name)
    save_mesh_copy(other_trimesh, output_dir / other_name)
    print(f"原始模型已保存: {output_dir / main_name}, {output_dir / other_name}")

    # 计算差集
    result_manifold = main_manifold - other_manifold
    result_trimesh = manifold_to_trimesh(result_manifold)

    # 保存结果
    result_path = output_dir / "diff_result.glb"
    save_mesh_copy(result_trimesh, result_path)
    print(f"差集结果已保存: {result_path}")

def difference_many(input_paths, output_dir):
    """
    对多个模型进行连续差集：第一个减去后面所有，保存所有原始模型及最终结果。
    input_paths: 列表，第一个为主模型
    """
    if len(input_paths) < 2:
        raise ValueError("至少需要两个模型")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifolds = []
    trimeshes = []

    # 加载所有模型并保存原始副本
    for i, path in enumerate(input_paths):
        manifold, trimesh_obj = load_and_convert_to_manifold(path)
        manifolds.append(manifold)
        trimeshes.append(trimesh_obj)

        # 保存原始模型，按顺序命名
        orig_name = f"input_{i:02d}_{Path(path).stem}_original.glb"
        save_mesh_copy(trimesh_obj, output_dir / orig_name)
        print(f"原始模型已保存: {output_dir / orig_name}")

    # 连续差集：从第一个开始依次减去后面的
    result_manifold = manifolds[0]
    for i in range(1, len(manifolds)):
        result_manifold = result_manifold - manifolds[i] 

    result_trimesh = manifold_to_trimesh(result_manifold)
    result_path = output_dir / "diff_result.glb"
    save_mesh_copy(result_trimesh, result_path)
    print(f"差集结果已保存: {result_path}")


def difference_two_meshes(main_mesh: Trimesh, other_mesh: Trimesh,
                          engine: str = 'blender', fallback_engines=['manifold', 'cork']) -> Optional[Trimesh]:
    """
    计算 main_mesh - other_mesh 的差集，返回处理后的 trimesh.Trimesh。
    使用 trimesh 自带的布尔运算，优先使用指定引擎（默认 manifold），失败时依次尝试 fallback_engines。

    :param main_mesh: 被减的网格（必须是有效的 Trimesh）
    :param other_mesh: 减去的网格（必须是有效的 Trimesh）
    :param engine: 首选布尔引擎，可选 'manifold', 'blender', 'cork' 等
    :param fallback_engines: 首选引擎失败时依次尝试的引擎列表
    :return: 差集结果网格，失败时返回 None
    """
    if not isinstance(main_mesh, trimesh.Trimesh) or not isinstance(other_mesh, trimesh.Trimesh):
        raise TypeError("Both inputs must be trimesh.Trimesh")

    # 预处理：清理输入网格，提高布尔成功率
    def clean_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        mesh = mesh.copy()
        mesh.merge_vertices()
        mesh.remove_degenerate_faces()
        trimesh.repair.fix_normals(mesh)
        if not mesh.is_watertight:
            trimesh.repair.fill_holes(mesh)
        return mesh

    main_clean = clean_mesh(main_mesh)
    other_clean = clean_mesh(other_mesh)

    # 按优先级尝试各个引擎
    engines_to_try = [engine] + fallback_engines
    for eng in engines_to_try:
        try:
            result = main_clean.difference(other_clean, engine=eng)
            if result is None or result.is_empty:
                logging.warning(f"Boolean difference with engine '{eng}' returned empty result.")
                continue
            # 后处理：清理结果网格
            result.merge_vertices()
            result.remove_degenerate_faces()
            trimesh.repair.fix_normals(result)
            if result.volume < 0:
                result.invert()
            return result
        except Exception as e:
            logging.warning(f"Boolean difference with engine '{eng}' failed: {e}")
            continue

    logging.error("All boolean engines failed for difference operation.")
    return None
# def difference_two_meshes(main_mesh:Trimesh, other_mesh:Trimesh):
    """
    计算 main_mesh - other_mesh 的差集，返回处理后的 trimesh.Trimesh。
    main_mesh, other_mesh: trimesh.Trimesh 或 manifold3d.Manifold
    返回: 处理后的 trimesh.Trimesh
    """
    # 转换为 manifold3d.Manifold
    if isinstance(main_mesh, trimesh.Trimesh):
        verts = main_mesh.vertices.astype(np.float32)
        faces = main_mesh.faces.astype(np.uint32)
        mesh = m3d.Mesh(vert_properties=verts, tri_verts=faces)
        main_manifold = m3d.Manifold(mesh)
    elif isinstance(main_mesh, m3d.Manifold):
        main_manifold = main_mesh
    else:
        raise TypeError("main_mesh must be trimesh.Trimesh or manifold3d.Manifold")

    if isinstance(other_mesh, trimesh.Trimesh):
        verts = other_mesh.vertices.astype(np.float32)
        faces = other_mesh.faces.astype(np.uint32)
        mesh = m3d.Mesh(vert_properties=verts, tri_verts=faces)
        other_manifold = m3d.Manifold(mesh)
    elif isinstance(other_mesh, m3d.Manifold):
        other_manifold = other_mesh
    else:
        raise TypeError("other_mesh must be trimesh.Trimesh or manifold3d.Manifold")

    # 计算差集
    # result_manifold = main_manifold - other_manifold
    # result_trimesh = manifold_to_trimesh(result_manifold)
    result_trimesh=main_mesh.difference(other_mesh)
    return result_trimesh


def difference_many_meshes(mesh_list):
    """
    对多个 mesh 进行连续差集：第一个减去后面所有，返回处理后的 trimesh.Trimesh。
    mesh_list: list of trimesh.Trimesh 或 manifold3d.Manifold
    返回: 处理后的 trimesh.Trimesh
    """
    if len(mesh_list) < 2:
        raise ValueError("至少需要两个 mesh")

    manifolds = []
    for mesh in mesh_list:
        if isinstance(mesh, trimesh.Trimesh):
            verts = mesh.vertices.astype(np.float32)
            faces = mesh.faces.astype(np.uint32)
            m = m3d.Mesh(vert_properties=verts, tri_verts=faces)

            manifold = m3d.Manifold(m)
        elif isinstance(mesh, m3d.Manifold):
            manifold = mesh
        else:
            raise TypeError("mesh_list must contain trimesh.Trimesh or manifold3d.Manifold")
        manifolds.append(manifold)

    result_manifold = manifolds[0]
    for i in range(1, len(manifolds)):
        result_manifold = result_manifold - manifolds[i]

    result_trimesh = manifold_to_trimesh(result_manifold)
    return result_trimesh


import trimesh
# voxel_boolean_difference
def difference_two_meshes_2(mesh_a, mesh_b, pitch=None, resolution=100):
    """
    使用体素化方法计算 mesh_a - mesh_b

    Parameters:
    mesh_a, mesh_b: trimesh.Trimesh - 输入网格
    pitch: float - 体素大小（如果为None，则根据resolution自动计算）
    resolution: int - 网格分辨率（当pitch为None时使用）

    Returns:
    trimesh.Trimesh - 差集结果网格
    """
    # 1. 确定体素大小
    if pitch is None:
        # 根据两个网格的包围盒计算体素大小
        bounds = np.vstack([mesh_a.bounds, mesh_b.bounds])
        total_extents = bounds.max(axis=0) - bounds.min(axis=0)
        pitch = max(total_extents) / resolution

    # 2. 体素化两个网格
    voxel_a = mesh_a.voxelized(pitch=pitch)
    voxel_b = mesh_b.voxelized(pitch=pitch)

    # 3. 获取体素坐标（稀疏表示）
    # filled 属性返回所有被填充的体素坐标（体素索引空间）
    coords_a = voxel_a.encoding.sparse_indices  # 体素A的填充坐标
    coords_b = voxel_b.encoding.sparse_indices  # 体素B的填充坐标

    # 4. 在体素空间执行布尔差集：A - B
    # boolean_sparse 函数用于在两个稀疏体素坐标集上执行逻辑运算 [citation:2]
    from trimesh.voxel.ops import boolean_sparse
    coords_result = boolean_sparse(coords_a, coords_b, operation=np.logical_and)
    # 注意：这里用logical_and是因为我们想要A中不在B中的部分
    # 实际上需要的是 A and not B，但sparse操作需要分步或自定义

    # 更准确的做法是：手动计算 A - B
    # 将坐标转换为集合，便于计算差集
    set_a = set(map(tuple, coords_a))
    set_b = set(map(tuple, coords_b))
    set_result = set_a - set_b

    if not set_result:
        print("警告：差集结果为空")
        return None

    coords_result = np.array(list(set_result))

    # 5. 将稀疏坐标转换回体素网格
    from trimesh.voxel.ops import sparse_to_matrix, matrix_to_marching_cubes
    matrix_result = sparse_to_matrix(coords_result)

    # 6. 使用行进立方体算法重建表面网格 [citation:2]
    mesh_result = matrix_to_marching_cubes(matrix_result, pitch=pitch)

    # 7. 将网格移动到正确的位置（体素化原点）
    # 获取体素网格的原点（通常是最小包围盒的角点）
    origin_a = voxel_a.transform[:3, 3]
    mesh_result.apply_translation(origin_a)

    # 8. 清理结果网格
    mesh_result.remove_degenerate_faces()
    mesh_result.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh_result)

    return mesh_result



if __name__ == "__main__":
    # 示例用法
    base_dir = Path("app/services/test")
    output_two = base_dir / "output_two"
    output_many = base_dir / "output_many"

    # 测试两个模型
    difference_two(
        main_path=base_dir / "big_parks.glb",
        other_path=base_dir / "main_roads.glb",
        output_dir=output_two
    )

    # 测试多个模型
    difference_many(
        input_paths=[
            base_dir / "big_parks.glb",
            base_dir / "main_roads.glb",
            base_dir / "small_parks.glb"
        ],
        output_dir=output_many
    )

    # 使用示例
    sea = trimesh.primitives.Box(extents=[100, 100, 20])  # 海
    river = trimesh.primitives.Cylinder(radius=10, height=30)  # 河（完全穿透）

    result = difference_two_meshes(sea, river, resolution=200)
    if result:
        print(f"结果网格：{len(result.vertices)} 顶点，{len(result.faces)} 面")
        print(f"是否为实体：{result.is_volume}")
        result.export('sea_minus_river_voxel.glb')