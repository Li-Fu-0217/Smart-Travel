<template>
  <article v-if="card" class="itin-card">
    <header class="itin-head">
      <div class="head-main">
        <h4 class="itin-title">{{ card.title }}</h4>
        <span class="itin-dest">{{ card.destination }}</span>
      </div>
      <span class="itin-days">{{ card.dayCount }} 天</span>
    </header>
    <ol class="itin-days-list">
      <li v-for="d in card.days" :key="d.dayIndex" class="itin-day">
        <div class="day-head">
          <span class="day-no">第 {{ d.dayIndex }} 天</span>
          <span class="day-title">{{ d.title }}</span>
        </div>
        <ul class="day-items">
          <li v-for="(it, i) in d.items" :key="i">{{ it }}</li>
        </ul>
      </li>
    </ol>
    <footer class="itin-foot">
      <span v-for="t in card.tags" :key="t" class="tag">{{ t }}</span>
      <p v-if="card.tips" class="itin-tips">{{ card.tips }}</p>
    </footer>
  </article>
</template>

<script setup>
defineProps({
  card: { type: Object, default: null },
})
</script>

<style scoped>
.itin-card {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  padding: var(--sp-card-inner);
  border: 1px solid var(--line);
  border-radius: var(--r-card);
  background: var(--surface);
}
.itin-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--sp-card-gap);
}
.head-main {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
}
.itin-title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: var(--fs-h3);
}
.itin-dest {
  color: var(--muted);
  font-size: var(--fs-aux);
}
.itin-days {
  flex-shrink: 0;
  padding: 0 var(--sp-card-gap); line-height: 1.8;
  border-radius: var(--r-badge);
  background: var(--accent);
  color: var(--accent-ink);
  font-size: var(--fs-aux);
}
.itin-days-list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
}
.itin-day {
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
  padding-left: var(--sp-card-gap);
  border-left: 2px solid var(--line);
}
.day-head {
  display: flex;
  align-items: baseline;
  gap: var(--sp-card-gap);
}
.day-no {
  color: var(--accent);
  font-weight: 600;
  font-size: var(--fs-aux);
}
.day-title {
  font-weight: 600;
}
.day-items {
  margin: 0;
  padding-left: var(--sp-card-inner);
  color: var(--muted);
  font-size: var(--fs-aux);
  display: flex;
  flex-direction: column;
  gap: var(--sp-card-gap);
}
.itin-foot {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--sp-card-gap);
}
.tag {
  padding: 0 var(--sp-card-gap); line-height: 1.8;
  border: 1px solid var(--line);
  border-radius: var(--r-badge);
  background: var(--surface);
  color: var(--muted);
  font-size: var(--fs-aux);
}
.itin-tips {
  width: 100%;
  margin: 0;
  color: var(--muted);
  font-size: var(--fs-aux);
}
</style>
