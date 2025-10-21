<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">Insights</h3>
    <p>{{ insights }}</p>
  </section>
</template>

<script setup lang="ts">
interface Props {
  insights: string
}

defineProps<Props>();
</script>
