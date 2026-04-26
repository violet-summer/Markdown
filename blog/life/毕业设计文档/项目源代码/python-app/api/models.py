from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.model import ModelGenerateRequest
from app.services import model_service

router = APIRouter()


@router.get("", response_model=ApiResponse)
def list_models(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = model_service.list_models(db, user_id=current_user.id)
    return ApiResponse(code=200, message="OK", data=data)

@router.post("/generate", response_model=ApiResponse)
def generate_model(payload: ModelGenerateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = model_service.generate_model(db, user_id=current_user.id, layout_id=payload.layoutId, response_mode=payload.responseMode)
    return ApiResponse(code=200, message="OK", data=data)

@router.get("/scene/{scene_id}", response_model=ApiResponse)
def get_scene(scene_id: str):
    return ApiResponse(code=200, message="OK", data={"sceneId": scene_id})


@router.get("/{model_id}", response_model=ApiResponse)
def get_model(model_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = model_service.get_model_detail(db, user_id=current_user.id, model_id=model_id)
    if not data:
        raise HTTPException(status_code=404, detail="Model not found")
    return ApiResponse(code=200, message="OK", data=data)


@router.delete("/{model_id}", response_model=ApiResponse)
def delete_model(model_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = model_service.delete_model(db, user_id=current_user.id, model_id=model_id)
    if not data:
        raise HTTPException(status_code=404, detail="Model not found")
    return ApiResponse(code=200, message="OK", data=data)
