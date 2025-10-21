<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">Trend Analysis</h3>
    <p>{{ analysis }}</p>
  </section>
</template>

<script setup lang="ts">
interface Props {
  analysis: string
}

defineProps<Props>();
</script>
