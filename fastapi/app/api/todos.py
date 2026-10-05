"""行程待办接口（见施工规范 §4.5、§4.11）。

单条操作走顶层 /todos 路径；tripId 放在请求体（见 §4.11）。
"""
from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.common.result import Result
from app.core.deps import get_current_user, get_db, operation_log
from app.schemas.trip import TodoCreateRequest, TodoUpdateRequest
from app.services import todo_service

router = APIRouter(prefix="/todos", tags=["行程待办"])


@router.post("")
@operation_log("行程待办", "创建待办")
def create_todo(payload: TodoCreateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=todo_service.create_todo(db, current_user, payload))


@router.put("/{todo_id}")
@operation_log("行程待办", "修改待办")
def update_todo(todo_id: int, payload: TodoUpdateRequest, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=todo_service.update_todo(db, current_user, todo_id, payload))


@router.delete("/{todo_id}")
@operation_log("行程待办", "删除待办")
def delete_todo(todo_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    todo_service.delete_todo(db, current_user, todo_id)
    return Result()


@router.post("/{todo_id}/done")
@operation_log("行程待办", "打卡")
def done_todo(todo_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=todo_service.done(db, current_user, todo_id))


@router.post("/{todo_id}/undo")
@operation_log("行程待办", "撤销打卡")
def undo_todo(todo_id: int, request: Request, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return Result(data=todo_service.undo(db, current_user, todo_id))
