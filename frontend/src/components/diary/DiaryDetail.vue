<template>
  <UCard>
    <template #header>
      <DiaryHeader :entry="entry" />
    </template>

    <div class="space-y-8">
      <DiaryContent title="Mood Summary" :content="entry.moodSummary" />
      <DiaryContent title="Trend Analysis" :content="entry.trendAnalysis" />
      <DiaryContent title="Insights" :content="entry.insights" />
      <DiaryContent title="Practice" :content="entry.practice" />
      <Message :message="entry.message" :character-name="character?.name || 'AI'" />
      <EmotionRadar :emotion-scores="entry.emotionScores" />
    </div>
  </UCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { DiaryRecord } from '~/types';
import { CHARACTERS } from '~/constants/characters';

interface Props {
  entry: DiaryRecord
}

const props = defineProps<Props>();

const character = computed(() => CHARACTERS.find(c => c.id === props.entry.characterId));
</script>
