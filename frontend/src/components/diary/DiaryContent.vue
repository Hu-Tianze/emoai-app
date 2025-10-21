<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">{{ title }}</h3>
    <p>{{ content }}</p>
  </section>
</template>

<script setup lang="ts">
interface Props {
  title: string
  content: string
}

defineProps<Props>();
</script>
