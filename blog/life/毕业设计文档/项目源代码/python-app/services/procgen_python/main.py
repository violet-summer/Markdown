import logging

from app.services.procgen_python.custom_struct.json_layout import json_layout, layout_to_objs




def generate_from_artifacts(json_layout_path,output_dir_path):
    """从已编辑的artifacts（流线/多边形）生成3D模型"""
    json_layout_data = json_layout(json_path=json_layout_path)
    logging.info("开始载入json布局")
    json_layout_data.load_json()
    logging.info("结束载入json布局")
    layout_to_models=layout_to_objs(json_layout_data,output_dir_path)
    logging.info("开始转变布局为3D模型")
    # obj_models_path=layout_to_models.generate_obj()
    glb_models_path=layout_to_models.generate_glb()
    logging.info("结束转变布局为3D模型")
    # 只返回glb模型布局
    print(f"输出模型路径，{glb_models_path}")
    return  glb_models_path

