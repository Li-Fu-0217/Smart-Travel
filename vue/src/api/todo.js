// 行程待办接口（单条操作走顶层 /todos）
// 覆盖端点：POST /todos、PUT /todos/{id}、DELETE /todos/{id}、POST /todos/{id}/done、POST /todos/{id}/undo
import request from '../utils/request'

export function createTodo(data) {
  return request.post('/todos', data)
}

export function updateTodo(id, data) {
  return request.put(`/todos/${id}`, data)
}

export function deleteTodo(id) {
  return request.delete(`/todos/${id}`)
}

export function doneTodo(id) {
  return request.post(`/todos/${id}/done`)
}

export function undoTodo(id) {
  return request.post(`/todos/${id}/undo`)
}
