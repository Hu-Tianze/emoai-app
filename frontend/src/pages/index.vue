<template>
  <div class="home-page-content">
    <AppHeader />
    <div class="character-selection-wrapper">
      <div class="character-selection-area">
        <HomeCharacterGrid :characters="characters" />
      </div>
      <div class="more-text-container">
        <p class="more-text">More......</p>
      </div>
    </div>
    <HomeFooter />
  </div>
</template>

<script setup lang="ts">
import { CHARACTERS } from '~/constants/characters';
import AppHeader from '~/components/AppHeader.vue'; // 引用 AppHeader
import HomeFooter from '~/components/home/HomeFooter.vue';

const characters = CHARACTERS;

</script>

<style scoped>
.home-page-content {
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保内容区域占满父容器 */
}

.character-selection-wrapper {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 3rem 2rem; /* 48px 32px */
  position: relative; /* 允许内部元素定位 */
}

.character-selection-area {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.more-text-container {
  position: absolute;
  right: 5%; /* 调整为总宽度的 5% */
  top: 50%;
  transform: translateY(-50%);
}

.more-text {
  font-size: 1.125rem; /* 18px */
  color: var(--color-text-secondary); /* 浅色 */
  font-family: system-ui, -apple-system, sans-serif;
}

/* 移除 .footer-spacing 类 */
</style>
