import { defineStore } from 'pinia';
import type { ChatMessage } from '~/types';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as ChatMessage[],
  }),
  actions: {
    addMessage(message: ChatMessage) {
      this.messages.push(message);
    },
  },
});
