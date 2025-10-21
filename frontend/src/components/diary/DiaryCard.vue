<template>
  <UCard>
    <template #header>
      <NuxtLink :to="`/diary/${entry.date}`" class="font-bold text-lg">{{ entry.date }}</NuxtLink>
    </template>
    <p class="truncate">{{ entry.moodSummary }}</p>
    <template #footer>
      <div class="flex items-center">
        <UAvatar :src="character?.avatar" size="xs" class="mr-2" />
        <span>Chat with {{ character?.name }}</span>
      </div>
    </template>
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
