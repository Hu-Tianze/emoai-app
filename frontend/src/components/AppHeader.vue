<template>
  <div class="app-header">
    <div class="logo-section" @click="navigate('/')">
      <span class="logo-main">EMO AI</span>
      <span class="logo-sub">will always be with you</span>
    </div>
    <nav class="nav-section">
      <div class="nav-item" :class="{ active: isHomeOrChatActive }" @click="navigate(chatLink)">
        <img src="/icons/chat-icon.png" alt="Talk" class="nav-icon" >
        <span class="nav-text">Talk With Us</span>
      </div>
      <div class="nav-item" :class="{ active: isDiaryActive }" @click="navigate('/diary')">
        <img src="/icons/diary-icon.png" alt="Diary" class="nav-icon" >
        <span class="nav-text">Emotional Diary</span>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const chatLink = ref('/');

onMounted(() => {
  const lastCharacterId = localStorage.getItem('lastCharacterId');
  if (lastCharacterId) {
    chatLink.value = `/chat/${lastCharacterId}`;
  }
});

const navigate = (path: string) => {
  router.push(path).catch(err => {
    console.error(`[Navigation Error] Failed to navigate to '${path}':`, err);
  });
};

const isHomeOrChatActive = computed(() => route.path === '/' || route.path.startsWith('/chat'));
const isDiaryActive = computed(() => route.path.startsWith('/diary'));

</script>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.875rem;
  background-color: var(--color-header-bg);
  border-bottom: 1px solid var(--color-border);
}

.logo-section {
  display: flex;
  align-items: baseline;
  gap: 0.625rem;
  cursor: pointer;
}

.logo-main {
  font-size: 36px;
  font-weight: 500;
  color: var(--color-text-primary);
  font-family: system-ui, -apple-system, sans-serif;
}

.logo-sub {
  font-size: 20px;
  color: #7C6B57;
}

.nav-section {
  display: flex;
  gap: 2.5rem;
  position: relative;
  top: 4px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #8B8B8B;
  transition: color 0.2s;
  cursor: pointer;
}

.nav-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.nav-item:hover .nav-text {
  color: var(--color-text-primary);
}

.nav-item.active .nav-text {
  color: var(--color-text-primary);
  font-weight: 600;
}

.nav-item.active .nav-icon {
  transform: scale(1.1);
}

.nav-icon {
  width: 30px;
  height: 30px;
  transition: transform 0.2s;
}
</style>
