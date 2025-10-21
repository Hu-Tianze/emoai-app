<template>
  <div class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
    <div
      class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg"
      :class="message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'"
    >
      <p>{{ message.content }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage as ChatMessageType } from '~/types';

interface Props {
  message: ChatMessageType
}

defineProps<Props>();
</script>
