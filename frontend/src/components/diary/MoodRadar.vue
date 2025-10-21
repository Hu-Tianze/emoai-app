<template>
  <div class="space-y-6 py-6">
    <!-- 情绪雷达图 -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h3 class="text-lg font-semibold mb-4">Emotion Radar</h3>
      <div class="flex justify-center">
        <div
          class="w-48 h-48 rounded-full border-2 border-purple-200 flex items-center justify-center"
        >
          <p class="text-center text-sm text-gray-600">
            Radar Chart<br>
            <span class="text-xs">(实现中)</span>
          </p>
        </div>
      </div>
    </div>

    <!-- 情绪评分 -->
    <div class="bg-white p-6 rounded-lg shadow">
      <h3 class="text-lg font-semibold mb-4">Emotion Scores</h3>
      <div class="space-y-2">
        <div
          v-for="(score, emotion) in emotionScores"
          :key="emotion"
          class="flex items-center gap-3"
        >
          <span class="w-20 text-sm font-semibold capitalize">{{ emotion }}</span>
          <div class="flex-1 bg-gray-200 rounded-full h-2">
            <div
              :style="{
                width: (score / 10) * 100 + '%',
                backgroundColor: emotionColor(emotion)
              }"
              class="h-2 rounded-full transition-all"
            />
          </div>
          <span class="w-12 text-right text-sm">{{ score }}/10</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EmotionScores, EmotionType } from '../../types';
import { EMOTION_COLORS } from '../../constants/emotions';

interface Props {
  emotionScores: EmotionScores
}

defineProps<Props>();

function emotionColor(emotion: string): string {
  return EMOTION_COLORS[emotion as EmotionType] || '#999';
}
</script>

<style scoped>
/* Emotion radar styles */
</style>
