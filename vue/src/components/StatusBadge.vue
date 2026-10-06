<template>
  <span class="status-badge" :class="'tone-' + tone">{{ label }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: { type: String, required: true },
  value: { type: [String, Number], required: true },
})

// 中文文案映射（§5.8 状态取值 + §7.7 图表中文标签）
const DICT = {
  booking: {
    pending: ['待确认', 'warn'],
    confirmed: ['已确认', 'ok'],
    cancelled: ['已取消', 'muted'],
    done: ['已完成', 'ok'],
  },
  alert: {
    open: ['待处理', 'danger'],
    handling: ['处理中', 'warn'],
    closed: ['已关闭', 'muted'],
  },
  alert_type: {
    lost: ['走失', 'danger'],
    illness: ['疾病', 'warn'],
    document: ['证件', 'warn'],
    accident: ['事故', 'danger'],
    other: ['其他', 'muted'],
  },
  signup: {
    registered: ['已报名', 'ok'],
    cancelled: ['已取消', 'muted'],
  },
  trip: { 1: ['进行中', 'ok'], 0: ['已归档', 'muted'] },
  todo: { 1: ['已完成', 'ok'], 2: ['待办', 'warn'] },
  traveler: { 1: ['正常', 'ok'], 0: ['停用', 'muted'] },
  catalog: { 1: ['上架', 'ok'], 0: ['下架', 'muted'] },
  tour: { 1: ['报名中', 'ok'], 0: ['已结束', 'muted'] },
  template: { 1: ['已发布', 'ok'], 0: ['已下架', 'muted'] },
  visibility: { 1: ['公开', 'ok'], 0: ['仅自己', 'muted'] },
  user: { 1: ['启用', 'ok'], 0: ['禁用', 'danger'] },
}

const entry = computed(() => DICT[props.type]?.[props.value] || [String(props.value), 'muted'])
const label = computed(() => entry.value[0])
const tone = computed(() => entry.value[1])
</script>

<style scoped>
.status-badge {
  display: inline-block;
  padding: 0 var(--sp-card-gap);
  border-radius: var(--r-badge);
  font-size: var(--fs-caption);
  font-family: var(--font-sans);
  line-height: 1.8;
  border: 1px solid currentColor;
}
.tone-ok { color: var(--ok); }
.tone-warn { color: var(--warn); }
.tone-danger { color: var(--danger); }
.tone-muted { color: var(--muted); }
</style>
