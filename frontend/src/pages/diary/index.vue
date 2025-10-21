<template>
  <div class="diary-page-container">
    <AppHeader />
    <div class="page-title-section">
      <img src="/icons/diary-icon.png" alt="Diary Icon" class="title-icon" >
      <h1 class="page-title">Your Emotional Diary</h1>
    </div>
    <main class="diary-main-content">
      <div class="column column-left">
        <DiaryList
          :diaries="diaries"
          :selected-diary-id="selectedDiaryId"
          @select-diary="handleSelectDiary"
        />
      </div>
      <div class="column column-middle">
        <EmotionReport
          v-if="selectedDiary"
          :diary="selectedDiary"
          :previous-diary="previousDiary"
        />
      </div>
      <div class="column column-right">
        <MoodRadarChart
          v-if="selectedDiary"
          :emotions="selectedDiary.emotions"
        />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import AppHeader from '~/components/AppHeader.vue';
import DiaryList from '~/components/diary/DiaryList.vue';
import EmotionReport from '~/components/diary/EmotionReport.vue';
import MoodRadarChart from '~/components/diary/MoodRadarChart.vue';
import { diaryEntries } from '~/constants/diaryData';

const diaries = ref(diaryEntries);
const selectedDiaryId = ref<string>(diaries.value[0]?.id ?? '');

const selectedDiary = computed(() => {
  return diaries.value.find(d => d.id === selectedDiaryId.value) || null;
});

const previousDiary = computed(() => {
  if (!selectedDiary.value) return null;
  const selectedIndex = diaries.value.findIndex(d => d.id === selectedDiaryId.value);
  // Since the array is reverse-chronological, the previous day is at the next index
  const isFirstEntry = selectedIndex === diaries.value.length - 1;
  return isFirstEntry ? null : diaries.value[selectedIndex + 1];
});

function handleSelectDiary(id: string) {
  selectedDiaryId.value = id;
}
</script>

<style scoped>
.diary-page-container {
  width: 100%;
  height: 100vh;
  background-color: var(--color-background);
  display: flex;
  flex-direction: column;
}

.page-title-section {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 0;
}

.title-icon {
  width: 32px;
  height: 32px;
}

.page-title {
  font-size: 1.75rem; /* 28px */
  font-weight: 500;
  color: var(--color-text-primary);
}

.diary-main-content {
  flex-grow: 1;
  display: flex;
  padding: 0 1.5rem 1.5rem; /* Adjust padding */
  gap: 1.5rem;
  overflow: hidden; /* Prevent layout shift from scrollbars */
}

.column {
  height: 100%;
  max-height: calc(100vh - 200px); /* Adjust based on header and title height */
}

.column-left {
  flex: 0 0 20%;
  min-width: 250px;
}

.column-middle {
  flex: 1 1 50%;
}

.column-right {
  flex: 0 0 30%;
  min-width: 300px;
}
</style>
