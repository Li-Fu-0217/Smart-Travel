<template>
  <div class="page">
    <h2 class="title">{{ profile.name || '档案详情' }}</h2>
    <div class="card">
      <div class="row"><span class="label">性别</span><span>{{ profile.gender || '-' }}</span></div>
      <div class="row"><span class="label">出生日期</span><span>{{ profile.birthDate || '-' }}</span></div>
      <div class="row"><span class="label">手机</span><span>{{ profile.phone || '-' }}</span></div>
      <div class="row"><span class="label">证件号</span><span>{{ profile.idCardNo || '-' }}</span></div>
      <div class="row"><span class="label">忌口</span><span>{{ profile.dietaryRestrictions || '-' }}</span></div>
      <div class="row"><span class="label">过敏</span><span>{{ profile.allergies || '-' }}</span></div>
      <div class="row"><span class="label">行动不便</span><span>{{ profile.mobilityNotes || '-' }}</span></div>
      <div class="row"><span class="label">紧急联系人</span><span>{{ profile.emergencyContact || '-' }} {{ profile.emergencyPhone || '' }}</span></div>
    </div>
    <div class="card">
      <div class="label">偏好标签</div>
      <PreferenceTags v-model="tags" :disabled="saving" />
      <el-button type="primary" class="save" :loading="saving" @click="saveTags">保存偏好</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getTravelerProfile, updatePreferences } from '../../api/traveler'
import PreferenceTags from '../../components/PreferenceTags.vue'

const route = useRoute()
const id = Number(route.query.id) || 0
const profile = ref({})
const tags = ref([])
const saving = ref(false)

async function load() {
  profile.value = await getTravelerProfile(id)
  tags.value = (profile.value.preferenceTags || '').split(',').filter(Boolean)
}

async function saveTags() {
  saving.value = true
  try {
    await updatePreferences(id, tags.value)
    ElMessage.success('已保存')
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.title { margin: 0; font-size: var(--fs-h2); }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); padding: var(--sp-card-inner); display: flex; flex-direction: column; gap: var(--sp-card-gap); }
.row { display: flex; gap: var(--sp-card-gap); }
.label { color: var(--muted); width: 90px; flex-shrink: 0; }
.save { min-height: var(--min-tap); }
</style>
