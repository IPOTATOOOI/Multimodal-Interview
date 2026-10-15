/**
 * API 配置
 * 从环境变量读取，避免硬编码
 */

// 后端 API 基础地址
// 【关键修改】用 ?? 替代 ||，空字符串会被保留，仅 undefined/null 才用兜底
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

// WebSocket 基础地址
// 同步修改，避免未来出问题
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL ?? 'ws://localhost:8765'

// Stable Diffusion 地址
// 同步修改，避免未来出问题
export const STABLE_DIFFUSION_URL =
  import.meta.env.VITE_STABLE_DIFFUSION_URL ?? 'http://localhost:7861'

// 完整的 API 端点生成器
export const getApiUrl = (path: string): string => {
  return `${API_BASE_URL}/api${path}`
}

// 完整的 WebSocket 端点生成器
export const getWsUrl = (path: string): string => {
  return `${WS_BASE_URL}${path}`
}
