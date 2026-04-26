from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.db.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.job import JobCreateRequest
from app.services import job_service

router = APIRouter()

@router.get("/{job_id}", response_model=ApiResponse)
def get_job(job_id: int, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = job_service.get_job(db, job_id, user_id=current_user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
    return ApiResponse(code=200, message="OK", data=data)


@router.post("", response_model=ApiResponse)
def create_job(payload: JobCreateRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    data = job_service.create_job(
        db,
        user_id=current_user.id,
        job_type=payload.type,
        payload_json=payload.payload,
    )
    return ApiResponse(code=200, message="OK", data=data)
