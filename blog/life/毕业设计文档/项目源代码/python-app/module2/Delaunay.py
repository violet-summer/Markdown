
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from scipy.spatial import Delaunay  # version 1.4.1


import cv2
import numpy as np
import math
import json
import os
import sys

def normalize_points(points, min_xy, max_xy, target_size=1000):
    points_arr = np.array(points)
    scale = max_xy - min_xy
    scale[scale == 0] = 1  # 防止除零
    norm_points = (points_arr - min_xy) / scale * target_size
    return norm_points.tolist()

#三角剖分和模型生成的部分
#——————————————————————————————————————————————————
def plot_polygon(ax, polygon_data, color):
    if not polygon_data or len(polygon_data) < 3:
        with open("polygon_error.log", "a", encoding="utf-8") as logf:
            logf.write(f"plot_polygon: 点数不足，无法绘制。数据: {polygon_data}\n")
        return
    lon_coords = [point['lon'] for point in polygon_data]
    lat_coords = [point['lat'] for point in polygon_data]
    polygon = Polygon(list(zip(lon_coords, lat_coords)), closed=True, fill=False, edgecolor=color)
    ax.add_patch(polygon)

def plot_triangle(ax, triangle_data, color):
    # Extract lon and lat coordinates from triangle data
    lon_coords = [triangle_data[key]['lon'] for key in ('p1', 'p2', 'p3')]
    lat_coords = [triangle_data[key]['lat'] for key in ('p1', 'p2', 'p3')]
    triangle = Polygon(list(zip(lon_coords, lat_coords)), closed=True, fill=False, edgecolor=color)
    ax.add_patch(triangle)

def point_cross_triangle_border(p0, p1, p2):
    # 判断p0为起始点，y轴向下方向的射线，是否与p1，p2线段相交
    cross_point_count = 0

    if p1['lon'] < p2['lon']:
        min_lon, max_lon = p1['lon'], p2['lon']
    else:
        min_lon, max_lon = p2['lon'], p1['lon']

    if p0['lon'] >= min_lon and p0['lon'] <= max_lon:
        # p0的x在p1和p2之间才有意义
        # 判断p1，p2的x是否一样
        if p1['lon'] == p2['lon']:
            # p1p2是一条垂直线
            # 不用检查p0是否在p1p2上
            cross_point_count += 0
        else:
            # p1p2不是垂直线，找到p1p2的方程式
            k = (p2['lat'] - p1['lat']) / (p2['lon'] - p1['lon'])
            b = p2['lat'] - k * p2['lon']
            crosspoint_y = p0['lon'] * k + b
            if p0['lat'] > crosspoint_y:
                cross_point_count += 1

    return cross_point_count


def check_point(i, p2, points):
    p1 = None
    p3 = None
    length = len(points)
    
    if i == 1:
        p1 = points[length - 1]
        p3 = points[i]
    elif i == length:
        p1 = points[i - 2]
        p3 = points[0]
    else:
        p1 = points[i - 2]
        p3 = points[i]

    v1 = {
        'x': p2['lon'] - p1['lon'],
        'y': p2['lat'] - p1['lat'],
        'z': 0
    }
    v2 = {
        'x': p3['lon'] - p2['lon'],
        'y': p3['lat'] - p2['lat'],
        'z': 0
    }

    z = v1['x'] * v2['y'] - v1['y'] * v2['x']

    if z < 0:
        print(f"点:({p2['lon']}, {p2['lat']})是凸点！")
        return True
    elif z == 0:
        print(f"点:({p2['lon']}, {p2['lat']})是平点！")
        return True
    else:
        print(f"点:({p2['lon']}, {p2['lat']})是凹点！")
        return False

def is_point_inside_triangle(p0, p1, p2, p3):
    def sign(p1, p2, p3):
        return (p1["lon"] - p3["lon"]) * (p2["lat"] - p3["lat"]) - (p2["lon"] - p3["lon"]) * (p1["lat"] - p3["lat"])

    d1 = sign(p0, p1, p2)
    d2 = sign(p0, p2, p3)
    d3 = sign(p0, p3, p1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)

def cut_polygon(points):
    # 会多次调用的图形切割方法
    # points为导入的点
    # 先判断这个图形是不是凸多边形
    is_convex = True
    convex_points = []  # 凸点数组
    for i in range(1, len(points) + 1):
        p2 = points[i - 1]

        if not check_point(i, p2, points):
            is_convex = False
        else:
            convex_points.append(i)

    result = {
        'convex': [],
        'triangles': []
    }

    if is_convex:
        # 是凸多边形，返回自身的点
        result['convex'] = points
        print("是凸多边形")
        return result
    else:
        # -----------------------
        # 是凹多边形，要递归切割
        print("是凹多边形")
        # -----------------------
        # 遍历凸点，找到一个能切割的点
        for point in convex_points:
            p1 = None
            p2 = None
            p3 = None
            length = len(points)
            p1_pos = -1  # 当前凸点及其两旁的点，在图形中的位置
            p2_pos = -1
            p3_pos = -1
            if point == 1:
                p1 = points[length - 1]
                p2 = points[0]
                p3 = points[1]
                p1_pos = length - 1
                p2_pos = 0
                p3_pos = 1
            elif point == length:
                p1 = points[length - 2]
                p2 = points[length - 1]
                p3 = points[0]
                p1_pos = length - 2
                p2_pos = length - 1
                p3_pos = 0
            else:
                p1 = points[point - 2]
                p2 = points[point - 1]
                p3 = points[point]
                p1_pos = point - 2
                p2_pos = point - 1
                p3_pos = point

            # 遍历points中除去p1、p2、p3的点，是否在p1p2p3的三角形内
            conflict = False
            for j in range(length):
                if j != p1_pos and j != p2_pos and j != p3_pos:
                    # 遍历到非p1p2p3的点的时候
                    # 把这个点从points中拿出来，检测在不在p1p2p3的三角形内
                    if is_point_inside_triangle(points[j], p1, p2, p3):
                        conflict = True

            # 遍历结束，查看冲突值，如果为true，则发生冲突，该点不能切割
            if conflict:
                print(p2, " 不是可划分点")
            else:
                print(p2, " 是可划分点")
                # 开始划分
                # 切割三角形出来
                tri_list = {
                    'p1': p1,
                    'p2': p2,
                    'p3': p3
                }
                # 切割新的多边形出来
                new_points = points.copy()
                new_points.pop(p2_pos)
                result2 = cut_polygon(new_points)
                result['convex'] = result2['convex']
                result['triangles'] = result2['triangles'].copy()
                result['triangles'].append(tri_list)
                # 停止循环
                break

        return result

def create_delauney(points, svg_output_path):
    # 创建一个路径对象，包含轮廓的全部点
    contour_path = MplPath(points)
    # create a Delauney object using (x, y)
    tri = Delaunay(points)
    
    # 找到所有三角形的中点
    tri_centers = np.mean(points[tri.simplices], axis=1)

    # 确定中点是否在轮廓路径内部
    is_inside = contour_path.contains_points(tri_centers)

    # 过滤掉不在轮廓内部的三角形
    tri_simplices_inside = tri.simplices[is_inside]
    
    # 输出网格 SVG
    fig, ax = plt.subplots()
    ax.triplot(points[:, 0], points[:, 1], tri_simplices_inside.copy(), c='black')
    ax.plot(points[:, 0], points[:, 1], 'o', c='green')
    ax.set_aspect('equal')
    ax.invert_yaxis()
    fig.savefig(svg_output_path, format='svg', bbox_inches='tight')
    plt.close(fig)

def find_pos(substring, vcontent):
    # 找到点的原地点的部分
    v_arr = vcontent.split('\nv ')
    for i, v_item in enumerate(v_arr):
        if substring == v_item:
            return i
    return -1


def read_data(json_data, output_dir, bottom_height):
    for info in json_data['buildingArray']:
        # 创建obj文件
        title_content = f"mtllib {info['name']}.mtl\no {info['name']}"
        mesh_svg_output_path = os.path.join(output_dir, f"{info['name']}-网格.svg")
        points = info['points']
        points_length = len(points)

        if info['pointsOrder'] == "reverse":
            # 逆时针排序，改为顺时针
            points.reverse()

        # v点
        v_content = ""
        # 获取基准点
        basic_point = info['center'] if 'center' in info else {'lon': points[0]['lon'], 'lat': points[0]['lat']}
        for point in points:
            new_lon = point['lon'] - basic_point['lon']
            new_lat = point['lat'] - basic_point['lat']
            v_content += f"\nv {new_lon} {point['height']} {new_lat}"
        for point in points:
            new_lon = point['lon'] - basic_point['lon']
            new_lat = point['lat'] - basic_point['lat']
            point['lon'] = new_lon
            point['lat'] = new_lat
            v_content += f"\nv {new_lon} {bottom_height} {new_lat}"

        # 贴图
        vt_content = "\nvt 0.625000 0.500000"
        # 法向量
        vn_content = "\nvn 0 1 0\nvn 0 -1 0"
        # 侧面
        for i in range(1, points_length + 1):
            point1 = points[i - 1]
            point2 = points[i - 1]
            point3 = points[i] if i < points_length else points[0]
            a = (bottom_height - point1['height']) * (point3['lat'] - point1['lat']) - (bottom_height - point1['height']) * (
                point2['lat'] - point1['lat'])
            b = 0
            c = (point2['lon'] - point1['lon']) * (bottom_height - point1['height']) - (
                point3['lon'] - point1['lon']) * (bottom_height - point1['height'])
            vn_content += f"\nvn {a} {b} {c}"

        # 生成面组
        face_content = "\ng box_Cube\nusemtl Material01\ns off"
        # 生成侧面
        side_face_content = ""
        for i in range(1, points_length + 1):
            side_face_content += "\nf "
            if i < points_length:
                side_face_content += f"{i}/1/{i + 2} {i + points_length}/1/{i + 2} {i + points_length + 1}/1/{i + 2} {i + 1}/1/{i + 2}"
            else:
                side_face_content += f"{i}/1/{i + 2} {i + points_length}/1/{i + 2} {1 + points_length}/1/{i + 2} 1/1/{i + 2}"

        # 生成顶面和底面（new！！）
        # 顶面
        top_face_content = ""
        # 底面
        bottom_face_content = ""

        # 获取切割结果
        cut_face = cut_polygon(points)
        print("三角切割结果")
        print(cut_face)
        lon_coords = [point['lon'] for point in cut_face['convex']]
        lat_coords = [point['lat'] for point in cut_face['convex']]
        lon_coords_tri = [triangle_data[key]['lon'] for triangle_data in cut_face['triangles'] for key in ('p1', 'p2', 'p3')]
        lat_coords_tri = [triangle_data[key]['lat'] for triangle_data in cut_face['triangles'] for key in ('p1', 'p2', 'p3')]

        fig, ax = plt.subplots()

        # Plot convex polygon
        plot_polygon(ax, cut_face['convex'], color='blue')

        # Plot triangles
        for triangle_data in cut_face['triangles']:
            plot_triangle(ax, triangle_data, color='red')

        # Set axis limits and labels
        ax.set_xlim(min(lon_coords + lon_coords_tri) - 20, max(lon_coords + lon_coords_tri) + 20)
        ax.set_ylim(min(lat_coords + lat_coords_tri) - 20, max(lat_coords + lat_coords_tri) + 20)
        ax.set_xlabel('Lon')
        ax.set_ylabel('Lat')
        ax.set_aspect('equal')
        ax.invert_yaxis()

        # Add legend
        # legend_elements = [Line2D([0], [0], color='blue', lw=2, label='Convex Polygon'),
        #                    Line2D([0], [0], color='red', lw=2, label='Triangle')]
        # ax.legend(handles=legend_elements)

        # 绘制三角剖分的结果
        # plt.show()

        # 这里还有点问题，要改
        # 已经处理了\nf 出现的问题
        # 生成切割后的凸多边形
        success_convex = False
        convex = cut_face['convex']
        for point in convex:
            substring = f"{point['lon']} {point['height']} {point['lat']}"
            num = find_pos(substring, v_content)
            if num != -1:
                top_face_content += f"{num}/1/1 "
                bottom_face_content = f"{num + points_length}/1/2 {bottom_face_content}"
                success_convex = True
            else:
                print("构造凸多边形的时候，出现了不存在的点")

        if success_convex:
            top_face_content = f"\nf {top_face_content}"
            bottom_face_content = f"\nf {bottom_face_content}"

        # 生成切割后的多个三角形
        triangles = cut_face['triangles']
        for tri in triangles:
            top_face_content += "\nf "
            for point in tri.values():
                substring = f"{point['lon']} {point['height']} {point['lat']}"
                num = find_pos(substring, v_content)
                if num != -1:
                    top_face_content += f"{num}/1/1 "
                    bottom_face_content = f"{num + points_length}/1/2 {bottom_face_content}"
                else:
                    print("构造三角形的时候，出现了不存在的点")
            bottom_face_content = f"\nf {bottom_face_content}"

        # 这里top_face_content和bottom_face_content添加"\n f"的方式不同是因为顶面和底面的点顺序不同
        # print('top_face_content',top_face_content);
        # print('bottom_face_content',bottom_face_content);
        # print('side_face_content',bottom_face_content)

        # obj文件统合
        obj_content = f"{title_content}{v_content}{vt_content}{vn_content}{face_content}{top_face_content}{bottom_face_content}{side_face_content}"
        # 创建mtl文件
        mtl_content = "newmtl Material01\nNs 50\nKa 1 1 1\nKd 0.800000 0.269435 0.285941\nKs 0.664835 0.664835 0.664835\nKe 0 0 0\nNi 1.450000\nd 1.000000\nillum 2"

        # 打印结果
        # print(obj_content)
        # print(mtl_content)

        # Python的文件生成方式
        obj_output_path = os.path.join(output_dir, f"{info['name']}-模型.obj")
        with open(obj_output_path, "w") as obj_file:
            obj_file.write(obj_content)

        # with open(f"{info['name']}.mtl", "w") as mtl_file:
        #     mtl_file.write(mtl_content)
        points_tuples = [(point['lon'], point['lat']) for point in points]
        points_tuples=np.array(points_tuples)
        create_delauney(points_tuples, mesh_svg_output_path)


#轮廓信息提取部分
#——————————————————————————————————————————————————
# 定义一个类来表示点对象
class Point:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

def find_contour_outlines(image):
    """
    找到图像外轮廓的点集，并按顺序连接成封闭轮廓

    参数：
    image：一个二维的numpy数组，代表图像。

    返回值：
    contour：一个numpy数组，表示轮廓点集，点按顺序连接可以还原图形的边界。
    """

    # 找到二值图像的轮廓和层级结构
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #print(contours)
    all_outlines = []
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.001 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        outline = approx.reshape(-1, 2)
        outline = np.vstack([outline, outline[0]])
        all_outlines.append(outline)

    return all_outlines


def build_building_array_from_outlines(outlines, name_prefix, top_height):
    building_array = []
    for idx, contour in enumerate(outlines, start=1):
        points = [Point(lon, lat).__dict__ for lon, lat in contour]
        points = points[:-1]
        for point in points:
            point['height'] = top_height
        building_array.append(
            {
                "name": f"{name_prefix}_Building{idx}",
                "points": points,
                "pointsOrder": "order",
                "center": {"lon": 0, "lat": 0},
            }
        )
    return building_array


def extract_outlines_from_filled_image(filled_image):
    mask = cv2.inRange(filled_image, (255, 0, 0), (255, 0, 0))
    bin_img = np.zeros_like(filled_image)
    bin_img[mask == 255] = [255, 255, 255]
    bin_img[mask != 255] = [0, 0, 0]

    gray = cv2.cvtColor(bin_img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(gray, kernel, iterations=1)
    dilation = cv2.erode(dilation, kernel, iterations=1)
    _, th = cv2.threshold(dilation, 127, 255, 0)
    outlines = find_contour_outlines(th)
    return outlines, bin_img, dilation


def generate_component_obj_svg(component_mask, name, output_dir, bottom_height, top_height):
    contours, hierarchy = cv2.findContours(component_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return

    loops = []
    unique_points = set()
    for contour in contours:
        if cv2.contourArea(contour) < 5:
            continue
        perimeter = cv2.arcLength(contour, True)
        epsilon = 0.001 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        pts = approx.reshape(-1, 2)
        if len(pts) < 3:
            continue
        loops.append(pts)
        for p in pts:
            unique_points.add((int(p[0]), int(p[1])))

    if len(unique_points) < 3:
        return

    points_arr = np.array(sorted(unique_points), dtype=float)
    tri = Delaunay(points_arr)
    tri_centers = np.mean(points_arr[tri.simplices], axis=1)

    h, w = component_mask.shape
    inside = []
    for c in tri_centers:
        x = int(round(c[0]))
        y = int(round(c[1]))
        if 0 <= x < w and 0 <= y < h and component_mask[y, x] > 0:
            inside.append(True)
        else:
            inside.append(False)
    tri_simplices_inside = tri.simplices[np.array(inside, dtype=bool)]

    point_to_idx = {(int(p[0]), int(p[1])): i for i, p in enumerate(points_arr)}
    n = len(points_arr)

    obj_path = os.path.join(output_dir, f"{name}-模型.obj")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write(f"o {name}\n")
        for p in points_arr:
            f.write(f"v {p[0]} {top_height} {p[1]}\n")
        for p in points_arr:
            f.write(f"v {p[0]} {bottom_height} {p[1]}\n")

        for s in tri_simplices_inside:
            a, b, c = int(s[0]) + 1, int(s[1]) + 1, int(s[2]) + 1
            f.write(f"f {a} {b} {c}\n")
            f.write(f"f {c + n} {b + n} {a + n}\n")

        for loop in loops:
            loop_len = len(loop)
            for i in range(loop_len):
                p1 = (int(loop[i][0]), int(loop[i][1]))
                p2 = (int(loop[(i + 1) % loop_len][0]), int(loop[(i + 1) % loop_len][1]))
                if p1 not in point_to_idx or p2 not in point_to_idx:
                    continue
                i1 = point_to_idx[p1] + 1
                i2 = point_to_idx[p2] + 1
                f.write(f"f {i1} {i2} {i2 + n} {i1 + n}\n")

    svg_path = os.path.join(output_dir, f"{name}-网格.svg")
    fig, ax = plt.subplots()
    if len(tri_simplices_inside) > 0:
        ax.triplot(points_arr[:, 0], points_arr[:, 1], tri_simplices_inside.copy(), c="black")
    for loop in loops:
        closed = np.vstack([loop, loop[0]])
        ax.plot(closed[:, 0], closed[:, 1], c="red", linewidth=1)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close(fig)


def generate_outputs_from_mask(mask_img, output_dir, prefix, bottom_height, top_height):
    num_labels, labels = cv2.connectedComponents(mask_img)
    for label in range(1, num_labels):
        component = np.where(labels == label, 255, 0).astype(np.uint8)
        if cv2.countNonZero(component) < 20:
            continue
        name = f"{prefix}_Building{label}"
        generate_component_obj_svg(component, name, output_dir, bottom_height, top_height)


def process_click_steps(input_image_path, output_dir, click_points, bottom_height, top_height):
    base_image = cv2.imread(input_image_path)
    if base_image is None:
        raise FileNotFoundError(f"无法读取输入图片: {input_image_path}")

    for step_idx in range(1, len(click_points) + 1):
        step_dir = os.path.join(output_dir, f"step_{step_idx}")
        os.makedirs(step_dir, exist_ok=True)

        work_img = base_image.copy()
        current_point = click_points[step_idx - 1]
        mask_tmp = np.zeros((work_img.shape[0] + 2, work_img.shape[1] + 2, 1), np.uint8)
        cv2.floodFill(work_img, mask_tmp, current_point, (255, 0, 0), (30, 30, 30), (30, 30, 30), cv2.FLOODFILL_FIXED_RANGE)

        outlines, bin_img, dilation = extract_outlines_from_filled_image(work_img)
        cv2.imwrite(os.path.join(step_dir, "processed_mask.png"), bin_img)
        cv2.imwrite(os.path.join(step_dir, "dilation.png"), dilation)
        cv2.imwrite(os.path.join(step_dir, "floodfill.png"), work_img)

        json_data = {"buildingArray": build_building_array_from_outlines(outlines, f"step{step_idx}", top_height)}
  
        if json_data["buildingArray"]:
            read_data(json_data, step_dir, bottom_height)
        

    final_dir = os.path.join(output_dir, "final_merged")
    os.makedirs(final_dir, exist_ok=True)

    # # 合并所有步骤生成的OBJ文件
    # merged_obj_path = os.path.join(final_dir, "final_merged_all.obj")
    # with open(merged_obj_path, "w", encoding="utf-8") as fout:
    #     for step_idx in range(1, len(click_points) + 1):
    #         step_dir = os.path.join(output_dir, f"step_{step_idx}")
    #         for fname in os.listdir(step_dir):
    #             if fname.endswith("-模型.obj"):
    #                 with open(os.path.join(step_dir, fname), "r", encoding="utf-8") as fin:
    #                     fout.write(fin.read())
    #                     fout.write("\n")

    # 其它输出（如合并轮廓的PNG等）可保留，但不再生成合并轮廓OBJ
    # work_img = base_image.copy()
    # for p in click_points:
    #     mask_tmp = np.zeros((work_img.shape[0] + 2, work_img.shape[1] + 2, 1), np.uint8)
    #     cv2.floodFill(work_img, mask_tmp, p, (255, 0, 0), (30, 30, 30), (30, 30, 30), cv2.FLOODFILL_FIXED_RANGE)

    # outlines, bin_img, dilation = extract_outlines_from_filled_image(work_img)
    # cv2.imwrite(os.path.join(final_dir, "processed_mask.png"), bin_img)
    # cv2.imwrite(os.path.join(final_dir, "dilation.png"), dilation)
    # cv2.imwrite(os.path.join(final_dir, "floodfill.png"), work_img)
    # 不再生成合并轮廓OBJ

# 全局变量
g_window_name = "contourImg"  # 窗口名
g_window_wh = [800, 600]  # 窗口宽高

g_location_win = [0, 0]  # 相对于大图，窗口在图片中的位置
location_win = [0, 0]  # 鼠标左键点击时，暂存g_location_win
g_location_click, g_location_release = [0, 0], [0, 0]  # 相对于窗口，鼠标左键点击和释放的位置

g_zoom, g_step = 1, 0.1  # 图片缩放比例和缩放系数
g_image_original = None
g_image_zoom = None
g_image_show = None


mask_original = None
g_click_points = []

p = 0

# 矫正窗口在图片中的位置
# img_wh:图片的宽高, win_wh:窗口的宽高, win_xy:窗口在图片的位置
def check_location(img_wh, win_wh, win_xy):
    for i in range(2):
        if win_xy[i] < 0:
            win_xy[i] = 0
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] > win_wh[i]:
            win_xy[i] = img_wh[i] - win_wh[i]
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] < win_wh[i]:
            win_xy[i] = 0
    # print(img_wh, win_wh, win_xy)


# 计算缩放倍数
# flag：鼠标滚轮上移或下移的标识, step：缩放系数，滚轮每步缩放0.1, zoom：缩放倍数
def count_zoom(flag, step, zoom):
    if flag > 0:  # 滚轮上移
        zoom += step
        if zoom > 1 + step * 20:  # 最多只能放大到3倍
            zoom = 1 + step * 20
    else:  # 滚轮下移
        zoom -= step
        if zoom < step:  # 最多只能缩小到0.1倍
            zoom = step
            # print(zoom)
    zoom = round(zoom, 2)  # 取2位有效数字
    return zoom

def mouse(event,x,y,flags,param): #鼠标事件回调函数
    global g_location_click, g_location_release, g_image_show, g_image_zoom, g_location_win, location_win, g_zoom, p, g_click_points
    #参数 （事件，x轴位置，y轴位置，标记，属性）
    """
    event:
        EVENT_MOUSEMOVE 0            #滑动
        EVENT_LBUTTONDOWN 1          #左键点击
        EVENT_RBUTTONDOWN 2          #右键点击
        EVENT_MBUTTONDOWN 3          #中键点击
        EVENT_LBUTTONUP 4            #左键放开
        EVENT_RBUTTONUP 5            #右键放开
        EVENT_MBUTTONUP 6            #中键放开
        EVENT_LBUTTONDBLCLK 7        #左键双击
        EVENT_RBUTTONDBLCLK 8        #右键双击
        EVENT_MBUTTONDBLCLK 9        #中键双击
    x,y:
        x,y，代表鼠标位于窗口的（x，y）坐标位置
    flags:
        代表鼠标的拖拽事件，以及键盘鼠标联合事件
        EVENT_FLAG_LBUTTON 1       #左鍵拖曳
        EVENT_FLAG_RBUTTON 2       #右鍵拖曳
        EVENT_FLAG_MBUTTON 4       #中鍵拖曳
        EVENT_FLAG_CTRLKEY 8       #(8~15)按Ctrl不放事件
        EVENT_FLAG_SHIFTKEY 16     #(16~31)按Shift不放事件
        EVENT_FLAG_ALTKEY 32       #(32~39)按Alt不放事件
        比如：按住CTRL键 单击左键  返回8+1=9
    :param param:不知道有什么用
    """
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        g_location_click = [x, y]  # 左键点击时，鼠标相对于窗口的坐标
        location_win = [g_location_win[0], g_location_win[1]]  # 窗口相对于图片的坐标，不能写成location_win = g_location_win

    elif event==cv2.EVENT_RBUTTONDOWN :
        g_original_h, g_original_w = g_image_zoom.shape[0:2]
        # 需要处理的mask区域设置为0，不考虑的地方设置为1
        mask = np.zeros((g_original_h + 2, g_original_w + 2, 1), np.uint8)
        mask[150:250, 150:250] = 0
        # print('mask')
        # print(mask)
        cv2.floodFill(g_image_zoom, mask, (g_location_win[0]+x, g_location_win[1]+y), (255, 0, 0), (30, 30, 30), (30, 30, 30), cv2.FLOODFILL_FIXED_RANGE)
        # cv2.circle(g_image_zoom,(g_location_win[0]+x, g_location_win[1]+y),20,255,-1)
        print('鼠标点击的坐标')
        print((x,y))
        print((g_location_win[0]+x, g_location_win[1]+y))

        g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + g_window_wh[1],
                       g_location_win[0]:g_location_win[0] + g_window_wh[0]]  # 实际的显示图片

        # 在滚轮缩放时，g_image_zoom利用原图重新刷新，所以需要利用缩放仿射变换，对原图同样的地方进行泛洪填充
        scale = g_image_zoom.shape[1]/g_image_original.shape[1]
        original_x = (g_location_win[0]+x)/scale
        original_y = (g_location_win[1]+y)/scale

        min_dist = float('inf')
        nearest_point = None
        for i in range(0 if 0 > math.floor(original_x) - 1 else math.floor(original_x)-1, math.ceil(original_x) + 1 if math.ceil(original_x) + 1 < g_image_original.shape[1] else g_image_original.shape[1]):
            for j in range(0 if 0 > math.floor(original_y) - 1 else math.floor(original_y) - 1, math.ceil(original_y) + 1 if math.ceil(original_y) + 1 < g_image_original.shape[0] else g_image_original.shape[0]):
                dist = math.sqrt((original_x - i) ** 2 + (original_y - j) ** 2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_point = (i, j)

        cv2.floodFill(g_image_original, mask_original, nearest_point, (255, 0, 0), (30, 30, 30),
                      (30, 30, 30), cv2.FLOODFILL_FIXED_RANGE)
        if nearest_point is not None:
            g_click_points.append(nearest_point)


    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        g_location_release = [x, y]  # 左键拖曳时，鼠标相对于窗口的坐标
        h1, w1 = g_image_zoom.shape[0:2]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        show_wh = [0, 0]  # 实际显示图片的宽高
        if w1 < w2 and h1 < h2:  # 图片的宽高小于窗口宽高，无法移动
            show_wh = [w1, h1]
            g_location_win = [0, 0]
        elif w1 >= w2 and h1 < h2:  # 图片的宽度大于窗口的宽度，可左右移动
            show_wh = [w2, h1]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
        elif w1 < w2 and h1 >= h2:  # 图片的高度大于窗口的高度，可上下移动
            show_wh = [w1, h2]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        else:  # 图片的宽高大于窗口宽高，可左右上下移动
            show_wh = [w2, h2]
            g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
            g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1],
                       g_location_win[0]:g_location_win[0] + show_wh[0]]  # 实际显示的图片
    elif event == cv2.EVENT_MOUSEWHEEL:  # 滚轮
        z = g_zoom  # 缩放前的缩放倍数，用于计算缩放后窗口在图片中的位置
        g_zoom = count_zoom(flags, g_step, g_zoom)  # 计算缩放倍数
        w1, h1 = [int(g_image_original.shape[1] * g_zoom), int(g_image_original.shape[0] * g_zoom)]  # 缩放图片的宽高
        w2, h2 = g_window_wh  # 窗口的宽高
        g_image_zoom = cv2.resize(g_image_original, (w1, h1), interpolation=cv2.INTER_AREA)  # 图片缩放
        show_wh = [w2, h2]  # 实际显示图片的宽高
        cv2.resizeWindow(g_window_name, w2, h2)

        g_location_win = [int((g_location_win[0] + x) * g_zoom / z - x),
                          int((g_location_win[1] + y) * g_zoom / z - y)]  # 缩放后，窗口在图片的位置
        check_location([w1, h1], [w2, h2], g_location_win)  # 矫正窗口在图片中的位置
        # print(g_location_win, show_wh)
        g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1],
                       g_location_win[0]:g_location_win[0] + show_wh[0]]  # 实际的显示图片

    cv2.imshow(g_window_name, g_image_show)

    # cv2.imshow("haha",g_image_original)

# 主函数
# def main(input_image_path, output_dir, bottom_height, top_height):
#     global g_image_original, g_image_zoom, g_image_show, mask_original, g_click_points

#     g_image_original = cv2.imread(input_image_path)
#     if g_image_original is None:
#         raise FileNotFoundError(f"无法读取输入图片: {input_image_path}")

#     g_image_zoom = g_image_original.copy()
#     g_image_show = g_image_original[
#         g_location_win[1]:g_location_win[1] + g_window_wh[1],
#         g_location_win[0]:g_location_win[0] + g_window_wh[0],
#     ]
#     mask_original = np.zeros((g_image_original.shape[0] + 2, g_image_original.shape[1] + 2, 1), np.uint8)
#     g_click_points = []

#     os.makedirs(output_dir, exist_ok=True)

#     floodfill_path = os.path.join(output_dir, "floodfill.png")
#     processed_mask_path = os.path.join(output_dir, "processed_mask.png")
#     dilation_path = os.path.join(output_dir, "dilation.png")
#     dilation_color_path = os.path.join(output_dir, "dilation_color.png")

#     # 设置窗口
#     cv2.namedWindow(g_window_name, cv2.WINDOW_NORMAL)
#     # 设置窗口大小，只有当图片大于窗口时才能移动图片
#     cv2.resizeWindow(g_window_name, g_window_wh[0], g_window_wh[1])
#     cv2.moveWindow(g_window_name, 500, 100)  # 设置窗口在电脑屏幕中的位置
#     # 鼠标事件的回调函数
#     cv2.setMouseCallback(g_window_name, mouse)
#     cv2.imshow(g_window_name, g_image_show)
#     cv2.waitKey()  # 不可缺少，用于刷新图片，等待鼠标操作

#     cv2.destroyAllWindows()
#     # 保存结果
#     cv2.imwrite(floodfill_path, g_image_zoom)

#     # 保留一次当前窗口态输出，便于回看交互结果
#     cv2.imwrite(processed_mask_path, g_image_original)

#     if not g_click_points:
#         print("未检测到右键泛洪点击，未生成步骤输出。")
#         return

#     process_click_steps(input_image_path, output_dir, g_click_points, bottom_height, top_height)
def main(input_image_path, output_dir, bottom_height, top_height, click_points_path,allow_reclick=True):
    global g_image_original, g_image_zoom, g_image_show, mask_original, g_click_points

    g_image_original = cv2.imread(input_image_path)
    if g_image_original is None:
        raise FileNotFoundError(f"无法读取输入图片: {input_image_path}")

    g_image_zoom = g_image_original.copy()
    g_image_show = g_image_original[
        g_location_win[1]:g_location_win[1] + g_window_wh[1],
        g_location_win[0]:g_location_win[0] + g_window_wh[0],
    ]
    mask_original = np.zeros((g_image_original.shape[0] + 2, g_image_original.shape[1] + 2, 1), np.uint8)
    g_click_points = []

    os.makedirs(output_dir, exist_ok=True)

    if allow_reclick:
        # 交互式点击
        cv2.namedWindow(g_window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(g_window_name, g_window_wh[0], g_window_wh[1])
        cv2.moveWindow(g_window_name, 500, 100)
        cv2.setMouseCallback(g_window_name, mouse)
        cv2.imshow(g_window_name, g_image_show)
        cv2.waitKey()
        cv2.destroyAllWindows()
        # 保存点击点
        with open(os.path.join(output_dir, "click_points.json"), "w", encoding="utf-8") as f:
            json.dump(g_click_points, f)
    else:
        # 直接读取保存的点击点
        if(click_points_path is not None):
            click_file = os.path.join(output_dir, "click_points.json")
        else:
            click_file = click_points_path
        if os.path.exists(click_file):
            with open(click_file, "r", encoding="utf-8") as f:
                g_click_points = json.load(f)
        else:
            print("未找到保存的点击点文件，无法继续。")
            return

    if not g_click_points:
        print("未检测到右键泛洪点击，未生成步骤输出。")
        return

    process_click_steps(input_image_path, output_dir, g_click_points, bottom_height, top_height)


def interface(input_image_path, output_dir, bottom_height, top_height,click_points_path,allow_reclick=True):
    main(input_image_path, output_dir, bottom_height, top_height,click_points_path,allow_reclick)

if __name__ == "__main__":
    # input_path = "F:\\CODE\\GIThub\\beijinglu\\origin\\minor.jpg"
    # output_dir = "F:\\CODE\\GIThub\\beijinglu\\result\\minor\\batch2"
    # bottom_height = 0.0
    # top_height = 100.0
    # main(input_path, output_dir, bottom_height, top_height)
    
    
    input_path = "F:\\CODE\\GIThub\\beijinglu\\origin\\2.bmp"
    output_dir = "F:\\CODE\\GIThub\\beijinglu\\result\\bmp\\batch11"
    bottom_height = 0.0
    top_height = 300.0
    main(input_path, output_dir, bottom_height, top_height, allow_reclick=True)
