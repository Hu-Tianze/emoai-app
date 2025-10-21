<template>
  <form class="p-4 border-t flex items-center" @submit.prevent="onSend">
    <UInput v-model="model" placeholder="Type a message..." class="flex-1 mr-4" />
    <UButton type="submit" icon="i-heroicons-paper-airplane" />
  </form>
</template>

<script setup lang="ts">
const model = defineModel<string>();
const emit = defineEmits(['send']);

const onSend = () => {
  emit('send');
};
</script>
