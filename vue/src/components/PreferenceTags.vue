<template>
  <div class="preference-tags" role="group" aria-label="偏好标签">
    <button
      v-for="tag in TAGS"
      :key="tag"
      type="button"
      class="tag"
      :class="{ active: modelValue.includes(tag) }"
      :aria-pressed="modelValue.includes(tag)"
      :disabled="disabled"
      @click="toggle(tag)"
    >
      {{ tag }}
    </button>
  </div>
</template>

<script setup>
// 固定 9 个偏好标签（§5.8），值就用这 9 个中文词，不要自创
const TAGS = ['海岛', '人文', '自然', '美食', '亲子', '摄影', '购物', '探险', '休闲']

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue'])

function toggle(tag) {
  if (props.disabled) return
  const next = props.modelValue.includes(tag)
    ? props.modelValue.filter((t) => t !== tag)
    : [...props.modelValue, tag]
  emit('update:modelValue', next)
}
</script>

<style scoped>
.preference-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--sp-card-gap);
}
.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: var(--min-tap);
  padding: 0 var(--sp-card-gap);
  border: 1px solid var(--line);
  border-radius: var(--r-badge);
  background: var(--surface);
  color: var(--muted);
  font-size: var(--fs-aux);
  font-family: var(--font-sans);
  cursor: pointer;
}
.tag:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.tag.active {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--accent-ink);
}
.tag:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
