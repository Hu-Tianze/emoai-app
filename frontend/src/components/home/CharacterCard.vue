<template>
  <NuxtLink :to="`/chat/${character.id}`" class="character-card">
    <img :src="character.avatar" :alt="character.name" class="avatar" >
    <p class="role-text">{{ character.role }}</p>
  </NuxtLink>
</template>

<script setup lang="ts">
import type { Character } from '~/types';

interface Props {
  character: Character
}

defineProps<Props>();
</script>

<style scoped>
.character-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: var(--color-text-primary); /* 深棕色 */
  /* 卡片宽度由 grid 决定，这里不再设置固定宽度 */
  padding: 1rem; /* 增加卡片内部间距，营造悬浮感 */
}

.avatar {
  width: 100%; /* 头像宽度占卡片宽度 */
  max-width: 12.5rem; /* 200px */
  height: auto;
  max-height: 15.625rem; /* 250px */
  object-fit: contain; /* 确保图片完整显示 */
  margin-bottom: 1.25rem; /* 20px */
  transition: transform 0.3s ease-in-out;
}

.character-card:hover .avatar {
  transform: scale(1.1);
}

.role-text {
  font-size: 1.25rem; /* 20px */
  font-weight: bold;
  text-align: center;
  font-family: system-ui, -apple-system, sans-serif; /* 使用系统字体 */
}
</style>
