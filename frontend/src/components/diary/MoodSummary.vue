<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">Mood Summary</h3>
    <p>{{ summary }}</p>
  </section>
</template>

<script setup lang="ts">
interface Props {
  summary: string
}

defineProps<Props>();
</script>
