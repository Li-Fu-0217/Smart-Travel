<template>
  <div class="chat">
    <div class="messages">
      <div class="placeholder">智能助手将在阶段 6 接入</div>
    </div>
    <div class="input-row">
      <el-input v-model="text" placeholder="输入消息..." class="input" @keyup.enter="send" />
      <el-button type="primary" @click="send">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const text = ref('')

function send() {
  if (!text.value.trim()) return
  ElMessage.info('智能助手将在阶段 6 接入')
  text.value = ''
}
</script>

<style scoped>
.chat { display: flex; flex-direction: column; gap: var(--sp-card-gap); min-height: 60vh; }
.messages { flex: 1; display: flex; align-items: center; justify-content: center; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); }
.placeholder { color: var(--muted); }
.input-row { display: flex; gap: var(--sp-card-gap); }
.input { flex: 1; }
</style>
