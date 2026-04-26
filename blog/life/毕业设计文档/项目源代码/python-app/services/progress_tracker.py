"""
进度跟踪服务 - 用于实时同步生成过程
"""
import json
from typing import Dict, Any
from datetime import datetime, timedelta

# 简单的内存存储（生产环境应使用 Redis）
_progress_store: Dict[str, Dict[str, Any]] = {}

def start_task(task_id: str, user_id: int) -> None:
    """启动新任务"""
    _progress_store[task_id] = {
        "status": "started",
        "user_id": user_id,
        "progress": 0,
        "phase": "Initializing",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "timeline": {},
    }
    print(f"[PROGRESS] Task {task_id} started", flush=True)

def update_progress(task_id: str, progress: int, phase: str, phase_time_ms: int = 0) -> None:
    """更新进度"""
    if task_id not in _progress_store:
        return
    
    store = _progress_store[task_id]
    store["progress"] = progress
    store["phase"] = phase
    store["timeline"][phase] = phase_time_ms
    
    print(f"[PROGRESS] Task {task_id}: {progress}% - {phase} ({phase_time_ms}ms)", flush=True)

def complete_task(task_id: str, result_data: Dict[str, Any]) -> None:
    """完成任务"""
    if task_id not in _progress_store:
        return
    
    store = _progress_store[task_id]
    store["status"] = "completed"
    store["progress"] = 100
    store["phase"] = "Completed"
    store["end_time"] = datetime.now().isoformat()
    store["result"] = result_data
    
    print(f"[PROGRESS] Task {task_id} completed", flush=True)

def fail_task(task_id: str, error: str) -> None:
    """任务失败"""
    if task_id not in _progress_store:
        return
    
    store = _progress_store[task_id]
    store["status"] = "failed"
    store["error"] = error
    store["end_time"] = datetime.now().isoformat()
    
    print(f"[PROGRESS] Task {task_id} failed: {error}", flush=True)

def get_progress(task_id: str) -> Dict[str, Any] | None:
    """获取任务进度"""
    return _progress_store.get(task_id)

def cleanup_old_tasks(max_age_hours: int = 24) -> None:
    """清理旧任务记录"""
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
    tasks_to_remove = []
    
    for task_id, store in _progress_store.items():
        if store.get("end_time"):
            end_time = datetime.fromisoformat(store["end_time"])
            if end_time < cutoff_time:
                tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove:
        del _progress_store[task_id]
        print(f"[PROGRESS] Cleaned up old task {task_id}", flush=True)
