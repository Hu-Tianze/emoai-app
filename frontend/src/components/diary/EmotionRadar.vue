<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">Emotion Radar</h3>
    <div>Chart will be here</div>
  </section>
</template>

<script setup lang="ts">
import type { EmotionScores } from '~/types';

interface Props {
  emotionScores: EmotionScores
}

defineProps<Props>();

// In a real app, you would use a charting library to render the radar chart.
</script>
