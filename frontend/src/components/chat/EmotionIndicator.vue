<template>
  <div class="p-4 border-t">
    <h3 class="font-semibold mb-2">Emotion Analysis</h3>
    <div class="flex justify-around">
      <div v-for="(score, emotion) in emotionScores" :key="emotion" class="text-center">
        <p class="capitalize">{{ emotion }}</p>
        <p class="font-bold">{{ score.toFixed(1) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EmotionScores } from '~/types';

interface Props {
  emotionScores: EmotionScores
}

defineProps<Props>();
</script>
