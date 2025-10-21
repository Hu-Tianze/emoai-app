// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs';

export default withNuxt(
  {
    rules: {
      // Vue 规则
      'vue/multi-word-component-names': 'off',
      'vue/max-attributes-per-line': ['error', { singleline: 3, multiline: 1 }],
      'vue/singleline-html-element-content-newline': 'off',
      'vue/html-indent': ['error', 2],

      // JavaScript/TypeScript 规则
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      'prefer-const': 'error',
      'no-var': 'error',

      // 注释规则
      'no-multi-spaces': 'error',
      'spaced-comment': ['error', 'always'],

      // 缩进和格式
      'indent': 'off',
      'comma-dangle': ['error', 'always-multiline'],
      'semi': ['error', 'always'],
      'quotes': 'off',

      // 导入规则
      'sort-imports': 'off', // 使用 prettier 处理

      // 行尾规则
      'eol-last': ['error', 'always'],
      'no-trailing-spaces': 'error',
    },
  },
);
