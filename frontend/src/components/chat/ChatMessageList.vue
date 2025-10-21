<template>
  <div class="space-y-4">
    <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage as ChatMessageType } from '~/types';

interface Props {
  messages: ChatMessageType[]
}

defineProps<Props>();
</script>
