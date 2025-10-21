<template>
  <div v-if="character" class="chat-page-container">
    <!-- 通用头部 -->
    <AppHeader />

    <!-- 主体内容区 -->
    <div class="chat-main-content">
      <!-- 左侧角色信息 -->
      <div class="chat-character-info">
        <img :src="character.avatar" :alt="character.name" class="chat-avatar">
        <p class="chat-role-text">{{ character.role }}</p>
        <button class="change-button" @click="goBack">
          <span class="change-icon">↻</span> Change
        </button>
      </div>

      <!-- 右侧对话气泡 -->
      <div class="chat-bubble-area">
        <div class="chat-bubble">
          <p class="bubble-text">
            My dear friend, what’s on your mind?
            Whatever you’d like to share, I’m here with you — always.
          </p>
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="chat-input-area">
      <input type="text" placeholder="Let’s begin our chat ~" class="chat-input">
      <div class="buttons-group">
        <button class="voice-button"><img src="/icons/audio-icon.png" alt="Voice" class="btn-icon"></button>
        <button class="send-button"><img src="/icons/send-icon.png" alt="Send" class="btn-icon"></button>
      </div>
    </div>
  </div>
  <div v-else>
    <p>Character not found. Redirecting...</p>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { CHARACTERS } from '~/constants/characters';
import AppHeader from '~/components/AppHeader.vue'; // 引入通用头部组件

const route = useRoute();
const router = useRouter();
const characterId = route.params.characterId as string;
const character = CHARACTERS.find(c => c.id === characterId);

// 如果角色不存在，重定向到首页
if (!character) {
  router.replace('/');
}

const goBack = () => {
  router.back();
};
</script>

<style scoped>
.chat-page-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--color-surface);
}

.chat-back-button {
  position: absolute;
  top: 1.25rem; /* 20px */
  left: 1.875rem; /* 30px */
  font-size: 1.5rem;
  color: var(--color-text-primary);
  background: none;
  border: none;
  cursor: pointer;
  z-index: 10; /* 确保在头部之上 */
}

.chat-main-content {
  flex-grow: 1;
  display: flex;
  padding: 2.5rem 1.875rem; /* 40px 30px */
  align-items: flex-start; /* 头像与气泡顶部对齐 */
  min-height: 0; /* Flexbox overflow fix */
}

.chat-character-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 25%; /* 约占内容区宽度的 25%~30% */
  margin-right: 3.125rem; /* 50px (头像与对话气泡间距) */
}

.chat-avatar {
  width: 15rem; /* 240px, 1.2x size */
  height: 15rem; /* 240px, 1.2x size */
  object-fit: contain;
  margin-bottom: 0.9375rem; /* 15px */
  margin-top: 0.5rem; /* Moved up 8px */
}

.chat-role-text {
  font-size: 1.25rem; /* 20px */
  font-weight: normal; /* 角色身份标签字重 */
  color: var(--color-text-secondary); /* 灰色 */
  margin-bottom: 0.75rem; /* 12px */
}

.change-button {
  font-size: 0.9375rem; /* 15px */
  color: #4FA3DA; /* 浅蓝灰 */
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem; /* 4px */
  transition: all 0.2s ease-in-out;
  margin-top: 6px; /* move down */
}

.change-button:hover {
  color: #0066CC; /* 深蓝 */
  text-decoration: underline;
}

.change-button:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.change-icon {
  font-size: 1rem; /* 16px */
}

.chat-bubble-area {
  flex-grow: 1;
  justify-content: flex-start;
  align-items: flex-start;
  padding-right: 1.875rem; /* 30px (对话气泡与右侧边距) */
  margin-top: 1.5rem; /* Increased top margin for spacing */
}

.chat-bubble {
  background-color: var(--color-bubble-bg);
  border: 1px solid var(--color-bubble-border);
  border-radius: 16px; /* 16px */
  padding: 12px 20px;
  max-width: 66%; /* Increased width */
  box-shadow: 0 2px 4px rgba(0,0,0,0.06); /* Added shadow */
}

.bubble-text {
  font-size: 1.125rem; /* 18px */
  color: #000000; /* 黑色 */
  font-weight: 500; /* 加粗 */
}

.chat-input-area {
  display: flex;
  align-items: center;
  gap: 0.75rem; /* Increased gap */
  padding: 0.75rem 1rem; /* 12px 16px */
  margin: 2rem auto; /* Center horizontally, increase vertical margin */
  height: 80px;
  width: 90%;
  max-width: 800px;
  background-color: transparent;
  border: 1px solid #E0D4C1;
  border-radius: 16px; /* Reduced from pill shape */
}

.chat-input {
  flex: 1;
  height: 100%;
  border: none;
  background-color: transparent;
  font-size: 1.125rem;
  outline: none;
  padding: 0 0.75rem;
  box-shadow: none;
}

.chat-input:focus {
  outline: none;
  box-shadow: none;
  border: none;
}

.chat-input::placeholder {
  color: #AAAAAA;
}

.buttons-group {
  display: flex;
  align-items: center;
  gap: 0.25rem; /* 4px */
}

.voice-button,
.send-button {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background-color: transparent;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  flex-shrink: 0;
}

.btn-icon {
  width: 32px;
  height: 32px;
}
</style>
