import os
import shutil
from pathlib import Path
from app.core.config import settings


def _run_procgen_artifacts(output_dir: Path) -> None:
    # 直接调用 Python 生成逻辑（假设已集成到 procgen_main.py）
    from app.services.procgen_python.main import generate_from_artifacts

    generate_from_artifacts(str(output_dir))


def generate_model(task_id: str, output_dir: str) -> dict:
    output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"Layout assets not found: {output_dir}")

    streamlines_path = output_dir / "streamlines.json"
    polygons_path = output_dir / "polygons.json"
    if streamlines_path.exists() or polygons_path.exists():
        _run_procgen_artifacts(output_dir)

    obj_sources = sorted(output_dir.glob("*.obj"))
    if not obj_sources:
        raise FileNotFoundError("No OBJ files found in layout output")

    # 只返回 OBJ 文件列表
    return {
        "task_id": task_id,
        "obj_files": [str(f) for f in obj_sources],
        "status": "success",
    }
