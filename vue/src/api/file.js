// 文件接口
// 覆盖端点：POST /files/upload、GET /files/download、GET /files/preview、DELETE /files
import request, { downloadFile } from '../utils/request'

export function uploadFile(formData) {
  return request.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function download(path) {
  return downloadFile('/files/download', { path })
}

export function preview(path) {
  return downloadFile('/files/preview', { path })
}

export function deleteFile(path) {
  return request.delete('/files', { params: { path } })
}
