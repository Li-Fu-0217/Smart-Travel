// 行程接口
// 覆盖端点：GET /trips、GET /trips/{id}、POST /trips、PUT /trips/{id}、DELETE /trips/{id}、
//           GET /trips/today、GET /trips/{tripId}/todos
import request from '../utils/request'

export function getTrips(params) {
  return request.get('/trips', { params })
}

export function getTrip(id) {
  return request.get(`/trips/${id}`)
}

export function createTrip(data) {
  return request.post('/trips', data)
}

export function updateTrip(id, data) {
  return request.put(`/trips/${id}`, data)
}

export function deleteTrip(id) {
  return request.delete(`/trips/${id}`)
}

export function getTripToday(travelerId) {
  return request.get('/trips/today', { params: { travelerId } })
}

export function getTripTodos(tripId) {
  return request.get(`/trips/${tripId}/todos`)
}
