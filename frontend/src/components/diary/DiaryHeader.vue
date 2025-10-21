<template>
  <div class="text-center py-4 border-b">
    <h2 class="text-3xl font-bold">{{ entry.date }}</h2>
    <div class="flex justify-center items-center mt-2">
      <UAvatar :src="character?.avatar" size="sm" />
      <p class="ml-2">A conversation with {{ character?.name }}</p>
    </div>
  </div>
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
