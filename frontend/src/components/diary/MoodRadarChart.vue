<template>
  <div class="mood-radar-chart-container">
    <h2 class="chart-title">Mood Radar Chart</h2>
    <v-chart class="chart" :option="option" autoresize />
    <div class="legend-container">
      <div v-for="(emotion, index) in emotionData" :key="emotion.name" class="legend-item">
        <span class="color-box" :style="{ backgroundColor: colors[index] }"/>
        <span class="legend-name">{{ emotion.name }}</span>
        <span class="legend-value">{{ emotion.value }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { use } from 'echarts/core';
import { RadarChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import VChart from 'vue-echarts';

// Register ECharts components
use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  RadarChart,
  CanvasRenderer,
]);

const props = defineProps<{
  emotions: Record<string, number>
}>();

const emotionLabels: Record<string, string> = {
  happy: 'Happy',
  content: 'Content',
  calm: 'Calm',
  anxious: 'Anxious',
  angry: 'Angry',
  sad: 'Sad',
};

const colors = ['#fbbf24', '#34d399', '#60a5fa', '#f87171', '#ef4444', '#a78bfa'];

const emotionData = computed(() => {
  return Object.entries(props.emotions).map(([key, value]) => ({
    name: emotionLabels[key],
    value: value,
  }));
});

const option = computed(() => ({
  tooltip: {
    trigger: 'item',
  },
  radar: {
    indicator: emotionData.value.map(e => ({ name: e.name, max: 100 })),
    shape: 'circle',
    splitNumber: 5,
    axisName: {
      color: '#8B8B8B',
      fontSize: 14,
    },
    splitLine: {
      lineStyle: {
        color: '#E0D0B8',
      },
    },
    splitArea: {
      areaStyle: {
        color: ['rgba(242, 215, 169, 0.2)', 'rgba(245, 232, 208, 0.2)'],
        shadowColor: 'rgba(0, 0, 0, 0.05)',
        shadowBlur: 10,
      },
    },
    axisLine: {
      lineStyle: {
        color: '#DDC8A0',
      },
    },
  },
  series: [
    {
      name: '情绪占比',
      type: 'radar',
      data: [
        {
          value: emotionData.value.map(e => e.value),
          name: '情绪占比',
        },
      ],
      areaStyle: {
        color: 'rgba(139, 94, 46, 0.2)',
      },
      lineStyle: {
        color: '#8B5E2E',
      },
      itemStyle: {
        color: '#8B5E2E',
      },
    },
  ],
}));

</script>

<style scoped>
.mood-radar-chart-container {
  padding: 1.5rem;
  background-color: #FBF6ED; /* A slightly lighter shade for contrast */
  border-radius: 1.25rem; /* 20px */
  height: 100%;
}

.chart-title {
  font-size: 1.5rem; /* 24px */
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 1.5rem;
  text-align: center;
}

.chart {
  height: 300px;
}

.legend-container {
  margin-top: 2rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  font-size: 1rem; /* 16px */
  color: var(--color-text-secondary);
}

.color-box {
  width: 1rem;
  height: 1rem;
  border-radius: 4px;
  margin-right: 0.75rem;
}

.legend-name {
  flex-grow: 1;
}

.legend-value {
  font-weight: 500;
  color: var(--color-text-primary);
}
</style>
