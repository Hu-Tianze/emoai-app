<template>
  <div class="p-4 border-b flex items-center">
    <UAvatar :src="character.avatar" :alt="character.name" />
    <h2 class="text-xl font-bold ml-4">{{ character.name }}</h2>
  </div>
</template>

<script setup lang="ts">
import type { Character } from '~/types';

interface Props {
  character: Character
}

defineProps<Props>();
</script>
