<template>
  <div class="emotion-report-container">
    <div class="report-header">
      <h1 class="report-date">{{ diary.date }}</h1>
    </div>

    <div class="report-section">
      <h2 class="section-title">Today's Mood Keywords</h2>
      <div class="keywords-container">
        <span v-for="keyword in moodKeywords" :key="keyword" class="keyword-tag">
          {{ keyword }}
        </span>
      </div>
    </div>

    <div class="report-section">
      <h2 class="section-title">Emotion Trend</h2>
      <p class="section-content">{{ emotionTrend }}</p>
    </div>

    <div class="report-section">
      <h2 class="section-title">Emotional Summary</h2>
      <p class="section-content">{{ diary.summary }}</p>
    </div>

    <div class="report-section">
      <h2 class="section-title">AI Observation</h2>
      <p class="section-content">{{ diary.observation }}</p>
    </div>

    <div class="report-section">
      <h2 class="section-title">Healing Exercise</h2>
      <p class="section-content">{{ diary.exercise }}</p>
    </div>

    <div class="report-section">
      <h2 class="section-title">AI's Message</h2>
      <p class="section-content message">{{ diary.message }}</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { getMoodKeywords } from '~/utils/diary';

// Define the structure of a diary entry for props
interface DiaryEntry {
  id: string;
  date: string;
  emotions: Record<string, number>;
  summary: string;
  observation: string;
  exercise: string;
  message: string;
}

const props = defineProps<{
  diary: DiaryEntry;
  previousDiary?: DiaryEntry | null;
}>();

const moodKeywords = computed(() => {
  return getMoodKeywords(props.diary.emotions);
});

const emotionTrend = computed(() => {
  if (!props.previousDiary) {
    return 'Today is a new beginning. Let’s take care of our emotional well-being together.';
  }

  const currentMainPositive = props.diary.emotions.happy + props.diary.emotions.calm;
  const prevMainPositive = props.previousDiary.emotions.happy + props.previousDiary.emotions.calm;

  if (currentMainPositive >= prevMainPositive) {
    return 'Your mood today is more relaxed and stable than yesterday. Although there are still feelings of anxiety, overall you are better able to take gentle care of yourself.';
  } else {
    return 'Compared to before, the fluctuations in your emotions seem more pronounced today, but this is a good opportunity for us to be aware.';
  }
});

</script>

<style scoped>
.emotion-report-container {
  padding: 2rem 2.5rem;
  height: 100%;
  overflow-y: auto;
  background-color: var(--color-surface);
}

.report-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.report-date {
  font-size: 2rem; /* 32px */
  font-weight: 500;
  color: var(--color-text-primary);
}

.report-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.25rem; /* 20px */
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.section-content {
  font-size: 1rem; /* 16px */
  color: #5a4a3a; /* A slightly darker text for readability */
  line-height: 1.8;
}

.section-content.message {
  font-style: italic;
  color: #7a6a5a;
}

.keywords-container {
  display: flex;
  gap: 1rem;
}

.keyword-tag {
  padding: 0.5rem 1rem;
  background-color: #F2D7A9;
  border-radius: var(--radius-full);
  font-size: 0.875rem; /* 14px */
  font-weight: 500;
  color: var(--color-text-primary);
  box-shadow: var(--shadow-sm);
}
</style>
