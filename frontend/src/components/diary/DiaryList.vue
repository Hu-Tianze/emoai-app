<template>
  <div class="diary-list-container">
    <h2 class="list-title">Diary Entries</h2>
    <div class="list-scroll-area">
      <button
        v-for="diary in diaries"
        :key="diary.id"
        class="diary-list-item"
        :class="{ selected: diary.id === selectedDiaryId }"
        @click="$emit('select-diary', diary.id)"
      >
        <span class="item-date">{{ diary.date }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface DiaryEntry {
  id: string;
  date: string;
  // other properties are not needed for this component
}

defineProps<{
  diaries: DiaryEntry[];
  selectedDiaryId: string;
}>();

defineEmits(['select-diary']);
</script>

<style scoped>
.diary-list-container {
  padding: 1.5rem;
  background-color: #FBF6ED;
  border-radius: 1.25rem; /* 20px */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.list-title {
  font-size: 1.5rem; /* 24px */
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
  text-align: center;
}

.list-scroll-area {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem; /* 12px */
  padding-right: 0.5rem; /* For scrollbar spacing */
}

.diary-list-item {
  width: 100%;
  padding: 1rem 1.25rem;
  border-radius: 0.75rem; /* 12px */
  background-color: #F5E8D0;
  border: 1px solid transparent;
  text-align: left;
  font-size: 1.125rem; /* 18px */
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.diary-list-item:hover {
  background-color: #F2D7A9;
  color: var(--color-text-primary);
}

.diary-list-item.selected {
  background-color: var(--color-header-bg);
  border-color: var(--color-border);
  color: var(--color-text-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

/* Custom scrollbar for the list */
.list-scroll-area::-webkit-scrollbar {
  width: 6px;
}

.list-scroll-area::-webkit-scrollbar-track {
  background: transparent;
}

.list-scroll-area::-webkit-scrollbar-thumb {
  background: #DDC8A0;
  border-radius: 3px;
}

.list-scroll-area::-webkit-scrollbar-thumb:hover {
  background: #C9B690;
}
</style>
