from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.layout import LayoutGenerateRequest, LayoutSaveRequest, LayoutArtifactsUpdateRequest, LayoutLayerEditRequest
from app.services import layout_service
from app.services import progress_tracker

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("", response_model=ApiResponse)
def list_layouts(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"[API] List layouts - user={current_user.id}")
    data = layout_service.list_layouts(db, user_id=current_user.id)
    return ApiResponse(code=200, message="OK", data=data)


@router.get("/{layout_id}", response_model=ApiResponse)
def get_layout(layout_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"[API] Get layout - user={current_user.id}, layout_id={layout_id}")
    data = layout_service.get_layout_detail(db, user_id=current_user.id, layout_id=layout_id)
    if not data:
        raise HTTPException(status_code=404, detail="Layout not found")
    return ApiResponse(code=200, message="OK", data=data)


@router.get("/{layout_id}/artifacts", response_model=ApiResponse)
def get_layout_artifacts(layout_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"[API] Get layout artifacts - user={current_user.id}, layout_id={layout_id}")
    data = layout_service.get_layout_artifacts(db, user_id=current_user.id, layout_id=layout_id)
    if not data:
        raise HTTPException(status_code=404, detail="Layout not found")
    return ApiResponse(code=200, message="OK", data=data)

@router.post("/generate", response_model=ApiResponse)
def generate_layout(payload: LayoutGenerateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    from uuid import uuid4
    task_id = str(uuid4())
    logger.info(f"[API] Generate layout - user={current_user.id}, mode={payload.responseMode}, task={task_id}")
    print(f"[BACKEND] POST /layout/generate - user={current_user.id}, task_id={task_id}", flush=True)
    
    try:
        data = layout_service.generate_layout(
            db,
            user_id=current_user.id,
            params_json=payload.params.model_dump(),
            response_mode=payload.responseMode,
            task_id=task_id,
            force_regenerate=payload.forceRegenerate,
        )
        print(f"[BACKEND] Generate result keys: {list(data.keys()) if isinstance(data, dict) else 'NOT A DICT'}", flush=True)
        print(f"[BACKEND] Generate result - taskId in data: {'taskId' in data if isinstance(data, dict) else 'N/A'}", flush=True)
        if isinstance(data, dict) and 'taskId' in data:
            print(f"[BACKEND] taskId value: {data['taskId']}", flush=True)
        response = ApiResponse(code=200, message="OK", data=data)
        print(f"[BACKEND] ApiResponse created, data.taskId={data.get('taskId', 'MISSING') if isinstance(data, dict) else 'N/A'}", flush=True)
        return response
    except Exception as e:
        print(f"[BACKEND] ERROR in /layout/generate: {str(e)}", flush=True)
        logger.error(f"Error generating layout: {str(e)}")
        raise

@router.get("/progress/{task_id}", response_model=ApiResponse)
def get_layout_progress(task_id: str, current_user = Depends(get_current_user)):
    """获取布局生成进度"""
    logger.info(f"[API] Get progress - user={current_user.id}, task={task_id}")
    progress = progress_tracker.get_progress(task_id)
    if not progress:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return ApiResponse(code=200, message="OK", data=progress)

@router.post("/save", response_model=ApiResponse)
def save_layout(payload: LayoutSaveRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    from uuid import uuid4
    task_id = str(uuid4()) if not hasattr(payload, 'taskId') else payload.taskId
    logger.info(f"[API] Save layout - user={current_user.id}, layout_id={payload.layoutId}, task={task_id}")
    data = layout_service.save_layout(
        db,
        user_id=current_user.id,
        layout_id=payload.layoutId,
        svg_content=payload.svgContent,
        response_mode=payload.responseMode,
        task_id=task_id,
    )
    return ApiResponse(code=200, message="OK", data=data)


@router.post("/{layout_id}/save-edit", response_model=ApiResponse)
def save_layout_edit(
    layout_id: int,
    payload: LayoutLayerEditRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存图层编辑 - 更新图层可见性并重新生成SVG"""
    logger.info(f"[API] Save layout edit - user={current_user.id}, layout_id={layout_id}")
    
    try:
        data = layout_service.save_layout_edit(
            db,
            user_id=current_user.id,
            layout_id=layout_id,
            layer_visibility=payload.layerVisibility,
            response_mode=payload.responseMode,
        )
        return ApiResponse(code=200, message="OK", data=data)
    except Exception as e:
        logger.error(f"Error saving layout edit: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{layout_id}/artifacts", response_model=ApiResponse)
def save_layout_artifacts(
    layout_id: int,
    payload: LayoutArtifactsUpdateRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"[API] Save layout artifacts - user={current_user.id}, layout_id={layout_id}")
    data = layout_service.save_layout_artifacts(
        db,
        user_id=current_user.id,
        layout_id=layout_id,
        streamlines=payload.streamlines,
        polygons=payload.polygons,
    )
    if not data:
        raise HTTPException(status_code=404, detail="Layout not found")
    return ApiResponse(code=200, message="OK", data=data)


@router.post("/{layout_id}/generate-3d", response_model=ApiResponse)
def generate_3d_model(
    layout_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """生成3D模型（OBJ文件）- 在编辑完SVG后调用"""
    from uuid import uuid4
    task_id = str(uuid4())
    logger.info(f"[API] Generate 3D model - user={current_user.id}, layout_id={layout_id}, task={task_id}")
    
    try:
        data = layout_service.generate_3d_model(
            db,
            user_id=current_user.id,
            layout_id=layout_id,
            task_id=task_id,
        )
        return ApiResponse(code=200, message="OK", data=data)
    except Exception as e:
        logger.error(f"Error generating 3D model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{layout_id}", response_model=ApiResponse)
def delete_layout(layout_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"[API] Delete layout - user={current_user.id}, layout_id={layout_id}")
    data = layout_service.delete_layout(db, user_id=current_user.id, layout_id=layout_id)
    if not data:
        raise HTTPException(status_code=404, detail="Layout not found")
    return ApiResponse(code=200, message="OK", data=data)
