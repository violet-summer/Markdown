import os
import shutil
import random
from pathlib import Path

# 定义源目录和目标目录
# 使用绝对路径以避免相对路径可能带来的问题
PROJECT_ROOT = Path("d:/feiyi_archi_yolo/archi-master")
RAW_IMAGES_DIR = PROJECT_ROOT / "raw" / "pictures"
RAW_LABELS_DIR = PROJECT_ROOT / "raw" / "pic_annt"
DATASET_ROOT = PROJECT_ROOT / "dataset2"

# 定义划分比例 (train:val = 8:2)
TRAIN_RATIO = 0.8

def setup_directories():
    """创建或清理目标目录结构"""
    if DATASET_ROOT.exists():
        print(f"清理旧数据集目录: {DATASET_ROOT}")
        shutil.rmtree(DATASET_ROOT)
    
    # 创建 images/train, images/val, labels/train, labels/val
    for split in ["train", "val"]:
        (DATASET_ROOT / "images" / split).mkdir(parents=True, exist_ok=True)
        (DATASET_ROOT / "labels" / split).mkdir(parents=True, exist_ok=True)
    
    print(f"已创建目录结构: {DATASET_ROOT}")

def get_file_pairs():
    """获取匹配的图片和标签文件对"""
    image_files = sorted(list(RAW_IMAGES_DIR.glob("*.jpg")))
    label_files = sorted(list(RAW_LABELS_DIR.glob("*.txt")))
    
    # 建立文件名（不含扩展名）到路径的映射
    img_map = {f.stem: f for f in image_files}
    lbl_map = {f.stem: f for f in label_files}
    
    # 找到共同的基础文件名
    common_stems = set(img_map.keys()) & set(lbl_map.keys())
    
    if not common_stems:
        print("错误: 未找到匹配的图片和标签文件！")
        return []
    
    pairs = []
    for stem in common_stems:
        pairs.append((img_map[stem], lbl_map[stem]))
        
    print(f"找到 {len(pairs)} 对匹配的图片和标签文件")
    if len(pairs) > 0:
        print("匹配示例 (前3对):")
        for i, (img, lbl) in enumerate(pairs[:3]):
            print(f"  {i+1}. 图片: {img.name} <--> 标签: {lbl.name}")
    
    # 检查是否有未匹配的文件并警告
    unmatched_imgs = set(img_map.keys()) - common_stems
    unmatched_lbls = set(lbl_map.keys()) - common_stems
    if unmatched_imgs:
        print(f"警告: {len(unmatched_imgs)} 张图片没有对应的标签文件 (已跳过)")
    if unmatched_lbls:
        print(f"警告: {len(unmatched_lbls)} 个标签文件没有对应的图片 (已跳过)")
        
    return pairs

def split_and_copy(pairs):
    """划分数据集并复制文件"""
    # 随机打乱
    random.seed(42) # 设置种子保证可复现
    random.shuffle(pairs)
    
    # 计算划分点
    split_idx = int(len(pairs) * TRAIN_RATIO)
    train_pairs = pairs[:split_idx]
    val_pairs = pairs[split_idx:]
    
    print(f"划分结果: 训练集 {len(train_pairs)} 张, 验证集 {len(val_pairs)} 张")
    
    # 复制文件的辅助函数
    def copy_files(file_pairs, split_name):
        print(f"正在复制 {split_name} 数据...")
        for img_src, lbl_src in file_pairs:
            # 目标文件名保持不变
            img_dst = DATASET_ROOT / "images" / split_name / img_src.name
            lbl_dst = DATASET_ROOT / "labels" / split_name / lbl_src.name
            
            shutil.copy2(img_src, img_dst)
            shutil.copy2(lbl_src, lbl_dst)
            
    copy_files(train_pairs, "train")
    copy_files(val_pairs, "val")

def main():
    print("开始重建数据集...")
    
    # 1. 检查源目录是否存在
    if not RAW_IMAGES_DIR.exists():
        print(f"错误: 图片源目录不存在 {RAW_IMAGES_DIR}")
        return
    if not RAW_LABELS_DIR.exists():
        print(f"错误: 标签源目录不存在 {RAW_LABELS_DIR}")
        return

    # 2. 准备目标目录
    setup_directories()
    
    # 3. 获取并匹配文件
    pairs = get_file_pairs()
    if not pairs:
        return
        
    # 4. 划分并复制
    split_and_copy(pairs)
    
    print("\n数据集重建完成！")
    print(f"数据集位置: {DATASET_ROOT}")
    print("目录结构:")
    print(f"  {DATASET_ROOT}/images/train")
    print(f"  {DATASET_ROOT}/images/val")
    print(f"  {DATASET_ROOT}/labels/train")
    print(f"  {DATASET_ROOT}/labels/val")

if __name__ == "__main__":
    main()
