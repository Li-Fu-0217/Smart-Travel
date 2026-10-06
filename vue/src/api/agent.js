// 智能助手接口（见施工规范 §6.4、§6.10）
// 覆盖端点：POST /agent/chat、GET /agent/sessions、GET /agent/sessions/{id}/messages
import request from '../utils/request'

export function agentChat(message, sessionId) {
  return request.post('/agent/chat', { message, sessionId })
}

export function getAgentSessions() {
  return request.get('/agent/sessions')
}

export function getAgentMessages(sessionId) {
  return request.get(`/agent/sessions/${sessionId}/messages`)
}
