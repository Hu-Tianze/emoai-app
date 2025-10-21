<template>
  <section>
    <h3 class="text-xl font-semibold mb-2">Practice</h3>
    <p>{{ practice }}</p>
  </section>
</template>

<script setup lang="ts">
interface Props {
  practice: string
}

defineProps<Props>();
</script>
