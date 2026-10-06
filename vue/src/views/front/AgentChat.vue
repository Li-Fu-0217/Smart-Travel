<template>
  <div class="chat-page">
    <header class="chat-head">
      <h2 class="title">智能助手</h2>
      <el-button text @click="newChat">新对话</el-button>
    </header>

    <div ref="msgBox" class="messages">
      <p v-if="!messages.length" class="empty">
        我是您的智能旅行助手，可以帮您查待办、约当地体验、推荐行程。
      </p>
      <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role">
        <div class="bubble">{{ m.content }}</div>
        <AgentThoughtSteps v-if="m.steps && m.steps.length" :steps="m.steps" />
        <ItineraryCard v-if="m.card" :card="m.card" />
        <div v-if="m.pendingConfirm" class="pending">
          <span class="pending-label">请点选预约时段：</span>
          <el-button v-for="s in m.pendingConfirm.options" :key="s" size="small" class="slot-btn" @click="selectSlot(s)">
            {{ s }}
          </el-button>
        </div>
      </div>
      <p v-if="loading" class="loading">思考中…</p>
    </div>

    <div class="input-row">
      <el-input
        v-model="input"
        placeholder="输入消息，例如：看看我家人这周的行程待办，顺便约个当地体验"
        class="input"
        :disabled="loading"
        @keyup.enter="send"
      />
      <el-button type="primary" :disabled="loading" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { agentChat, getAgentMessages } from '../../api/agent'
import { getSessionId, setSessionId, clearSessionId } from '../../utils/agentTools'
import AgentThoughtSteps from '../../components/AgentThoughtSteps.vue'
import ItineraryCard from '../../components/ItineraryCard.vue'

const messages = ref([])
const input = ref('')
const loading = ref(false)
const sessionId = ref('')
const msgBox = ref(null)
const route = useRoute()

async function sendText(text) {
  const t = (text || '').trim()
  if (!t || loading.value) return
  input.value = ''
  messages.value.push({ role: 'user', content: t })
  loading.value = true
  try {
    const resp = await agentChat(t, sessionId.value || null)
    sessionId.value = resp.sessionId
    setSessionId(resp.sessionId)
    messages.value.push({
      role: 'assistant',
      content: resp.reply,
      steps: resp.steps || [],
      card: resp.card || null,
      pendingConfirm: resp.pendingConfirm || null,
    })
  } catch {
    messages.value.pop()
  } finally {
    loading.value = false
    await nextTick()
    scrollBottom()
  }
}

function send() {
  sendText(input.value)
}

function selectSlot(slot) {
  sendText(`就约 ${slot}`)
}

function newChat() {
  clearSessionId()
  sessionId.value = ''
  messages.value = []
}

function scrollBottom() {
  if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight
}

onMounted(async () => {
  sessionId.value = getSessionId()
  if (sessionId.value) {
    try {
      const list = await getAgentMessages(sessionId.value)
      messages.value = list.map((m) => ({ role: m.role, content: m.content }))
      await nextTick()
      scrollBottom()
    } catch {
      clearSessionId()
      sessionId.value = ''
    }
  }
  // 首页搜索入口 / 目的地卡跳转携带 ?q=，自动发起一句提问
  const q = route.query.q
  if (q) sendText(String(q))
})
</script>

<style scoped>
.chat-page {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  height: calc(100vh - 180px);
  min-height: 60vh;
}
.chat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: var(--fs-h1);
}
.messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  padding: var(--sp-card-inner);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
}
.empty {
  margin: auto;
  color: var(--muted);
  text-align: center;
  max-width: 320px;
}
.msg {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  max-width: 86%;
}
.msg.user {
  align-self: flex-end;
}
.msg.assistant {
  align-self: flex-start;
}
.bubble {
  padding: var(--sp-card-gap) var(--sp-card-inner);
  border-radius: var(--r-card);
  line-height: 1.6;
}
.msg.user .bubble {
  background: var(--accent);
  color: var(--accent-ink);
}
.msg.assistant .bubble {
  background: var(--surface);
  border: 1px solid var(--line);
}
.pending {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--sp-card-gap);
}
.pending-label {
  color: var(--muted);
  font-size: var(--fs-aux);
}
.slot-btn {
  min-height: var(--min-tap);
}
.loading {
  color: var(--muted);
  font-size: var(--fs-aux);
}
.input-row {
  display: flex;
  gap: var(--sp-card-gap);
}
.input {
  flex: 1;
}
</style>
