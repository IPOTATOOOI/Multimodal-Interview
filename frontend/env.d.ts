/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_WS_BASE_URL?: string
  readonly VITE_STABLE_DIFFUSION_URL?: string
  readonly VITE_XUNFEI_APPID?: string
  readonly VITE_XUNFEI_API_KEY?: string
  readonly VITE_XUNFEI_API_SECRET?: string
  readonly VITE_SERPAPI_KEY?: string
  readonly VITE_AVATAR_APP_ID?: string
  readonly VITE_AVATAR_API_KEY?: string
  readonly VITE_AVATAR_API_SECRET?: string
  readonly VITE_AVATAR_SERVICE_ID?: string
  readonly VITE_AVATAR_ID?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
