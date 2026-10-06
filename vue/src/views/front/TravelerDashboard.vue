<template>
  <div class="page">
    <div class="toolbar">
      <h2 class="title">关怀看板</h2>
      <el-button type="primary" @click="bindVisible = true">绑定家人</el-button>
    </div>
    <div class="list">
      <router-link v-for="t in travelers" :key="t.id" :to="`/user/traveler-detail?id=${t.id}`" class="card">
        <div class="card-head">
          <span class="name">{{ t.name }}</span>
          <StatusBadge type="traveler" :value="t.status" />
        </div>
        <div v-if="t.preferenceTags" class="tags">{{ t.preferenceTags }}</div>
      </router-link>
      <p v-if="!travelers.length" class="muted">尚未绑定家人，点右上角「绑定家人」</p>
    </div>

    <el-dialog v-model="bindVisible" title="绑定家人" width="340px">
      <el-form label-width="80px">
        <el-form-item label="姓名"><el-input v-model="bindForm.name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="bindForm.phone" /></el-form-item>
        <el-form-item label="关系"><el-input v-model="bindForm.relation" placeholder="如：父亲" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bindVisible = false">取消</el-button>
        <el-button type="primary" @click="doBind">绑定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getMyTravelers, bindTraveler } from '../../api/family'
import StatusBadge from '../../components/StatusBadge.vue'

const travelers = ref([])
const bindVisible = ref(false)
const bindForm = reactive({ name: '', phone: '', relation: '' })

async function load() {
  travelers.value = await getMyTravelers()
}

async function doBind() {
  await bindTraveler(bindForm)
  bindVisible.value = false
  bindForm.name = ''; bindForm.phone = ''; bindForm.relation = ''
  ElMessage.success('绑定成功')
  load()
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.toolbar { display: flex; align-items: center; justify-content: space-between; }
.title { margin: 0; font-size: var(--fs-h2); }
.list { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.card { display: flex; flex-direction: column; gap: var(--sp-card-gap); background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); min-height: var(--min-tap); }
.card-head { display: flex; align-items: center; justify-content: space-between; }
.name { font-family: var(--font-serif); font-size: var(--fs-h3); }
.tags { color: var(--muted); font-size: var(--fs-aux); }
.muted { color: var(--muted); }
</style>
