<template>
  <UAlert
    :title="title"
    :description="description"
    :icon="icon"
    color="red"
    variant="subtle"
  />
</template>

<script setup lang="ts">
interface Props {
  title: string
  description: string
  icon?: string
}

withDefaults(defineProps<Props>(), {
  icon: 'i-heroicons-exclamation-triangle',
});
</script>
