<template>
  <section class="character-section">
    <HomeCharacterGrid :characters="characters" />
    <p class="more-roles-soon">更多角色敬请期待</p>
  </section>
</template>

<script setup lang="ts">
import { CHARACTERS } from '~/constants/characters';

const characters = CHARACTERS;
</script>

<style scoped>
.character-section {
  width: 100%;
}

.more-roles-soon {
  font-family: 'PingFang SC', sans-serif;
  font-size: 14px;
  color: #999999;
  text-align: center;
  margin-top: 50px;
}
</style>
