<template>
  <div class="flex flex-col h-full">
    <ChatHeader :character="character" />
    <ChatMessageList :messages="messages" class="flex-1 p-4" />
    <ChatInput v-model="newMessage" @send="sendMessage" />
  </div>
</template>

<script setup lang="ts">
import type { Character } from '~/types';
import { useChatStream } from '~/composables/useChatStream';

interface Props {
  character: Character
}

const props = defineProps<Props>();

// As per docs, useChatStream is preferred
const { messages, newMessage, sendMessage } = useChatStream(props.character.id);
</script>
