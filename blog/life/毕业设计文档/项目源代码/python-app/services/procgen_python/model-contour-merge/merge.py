from pathlib import Path

import trimesh
import numpy as np
import open3d as o3d
# 加载三个模型
mesh1 = trimesh.load('../assets/basic_geo/3/3.obj')  # 替换为实际路径
mesh2 = trimesh.load('../assets/basic_geo/2/2.obj')  # 替换为实际路径
mesh3 = trimesh.load('../assets/basic_geo/3/3.obj')  # 替换为实际路径

# 对第一个模型进行平移和旋转
translation1 = [20, 0, 0]  # x, y, z 平移
rotation_matrix1 = trimesh.transformations.rotation_matrix(
    angle=np.radians(30),  # 旋转角度
    direction=[0, 1, 0],   # 绕 y 轴旋转
    point=[0, 0, 0]        # 旋转中心
)
mesh1.apply_transform(rotation_matrix1)
mesh1.apply_translation(translation1)

# 对第二个模型进行平移和旋转
translation2 = [-40, 0, 30]
rotation_matrix2 = trimesh.transformations.rotation_matrix(
    angle=np.radians(45),
    direction=[0, 1, 0],   # 绕 y 轴旋转
    point=[0, 0, 0]
)
mesh2.apply_transform(rotation_matrix2)
mesh2.apply_translation(translation2)

# 对第三个模型进行平移和旋转
translation3 = [70, 0, -60]
rotation_matrix3 = trimesh.transformations.rotation_matrix(
    angle=np.radians(60),
    direction=[0, 1, 0],   # 绕 y 轴旋转
    point=[0, 0, 0]
)
mesh3.apply_transform(rotation_matrix3)
mesh3.apply_translation(translation3)

# 合并三个模型
merged_mesh = trimesh.util.concatenate([mesh1, mesh2, mesh3])

# 保存拼接后的模型
merged_mesh.export('./merged_trapezoid_mesh.obj')  # 替换为目标路径


print("模型梯形拼接完成，已保存为 merged_trapezoid_mesh.obj")

# transform, _ = trimesh.registration.icp(mesh1.vertices, mesh2.vertices,mesh3.vertices)
# mesh1.apply_transform(transform)  # 应用变换但仍是独立对象

# 可视化（保持独立）
scene = trimesh.Scene([mesh1, mesh2])
scene.show()


mesh1 = o3d.io.read_triangle_mesh(Path('../assets/basic_geo/3/3.obj'))  # 替换为实际路径
mesh2 = o3d.io.read_triangle_mesh(Path('../assets/basic_geo/2/2.obj'))  # 替换为实际路径
mesh3 = o3d.io.read_triangle_mesh(Path('../assets/basic_geo/3/3.obj'))  # 替换为实际路径

# 对第一个模型进行平移和旋转


mesh1.transform(rotation_matrix1)
mesh1.translate(translation1)

mesh2.transform(rotation_matrix2)
mesh2.translate(translation2)

mesh3.transform(rotation_matrix3)
mesh3.translate(translation3)

pcd1 = mesh1.sample_points_uniformly(number_of_points=1000)
pcd2 = mesh2.sample_points_uniformly(number_of_points=1000)
pcd3 = mesh3.sample_points_uniformly(number_of_points=1000)

init_transform = np.eye(4)

# 调整参数示例
result = o3d.pipelines.registration.registration_icp(
    pcd1, pcd2,
    max_correspondence_distance=20.0,  # 增大最大距离阈值
    init=np.eye(4),                   # 初始化为单位矩阵（无初始变换）
    estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
    criteria=o3d.pipelines.registration.ICPConvergenceCriteria(
        max_iteration=1000,           # 增加迭代次数
        relative_fitness=1e-6,       # 更严格的收敛条件
        relative_rmse=1e-6
    )
)
mesh1.transform(result.transformation)

# 可视化
# o3d.visualization.draw_geometries([mesh1, mesh2])


