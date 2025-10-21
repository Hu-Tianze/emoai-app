<template>
  <div class="text-center py-12">
    <div class="text-4xl mb-4">{{ icon }}</div>
    <h3 class="text-lg font-semibold">{{ title }}</h3>
    <p class="text-gray-500">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  description: string
}

defineProps<Props>();
</script>
