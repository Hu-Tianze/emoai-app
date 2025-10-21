<template>
  <div class="character-grid">
    <HomeCharacterCard v-for="character in characters" :key="character.id" :character="character" />
  </div>
</template>

<script setup lang="ts">
import type { Character } from '~/types';

interface Props {
  characters: Character[]
}

defineProps<Props>();
</script>

<style scoped>
.character-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 三列布局 */
  gap: 5%; /* 卡片间距约占总宽度的 5% */
  justify-items: center;
  align-items: start;
}
</style>
