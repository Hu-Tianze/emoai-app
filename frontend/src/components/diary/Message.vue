<template>
  <div class="bg-gray-100 p-4 rounded-lg">
    <p class="font-semibold">A message from {{ characterName }}:</p>
    <p class="italic">"{{ message }}"</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  message: string
  characterName: string
}

defineProps<Props>();
</script>
