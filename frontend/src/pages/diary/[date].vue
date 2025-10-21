<template>
  <div v-if="diaryEntry">
    <DiaryDetail :entry="diaryEntry" />
  </div>
  <div v-else>
    <UContainer class="py-12 text-center">
      <h2 class="text-2xl font-bold">Diary entry not found</h2>
      <UButton to="/diary" class="mt-4">Go back to Diary</UButton>
    </UContainer>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useDiary } from '~/composables/useDiary';

const route = useRoute();
const date = route.params.date as string;

const { diaryEntry, fetchDiary } = useDiary(date);

await fetchDiary();
</script>
