import { expect, afterEach, vi } from 'vitest'
import { cleanup } from '@vue/test-utils'

// 自动清理
afterEach(() => {
  cleanup()
})

// 全局配置
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))
