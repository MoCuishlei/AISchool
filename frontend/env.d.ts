/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_DESCRIPTION: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_ENABLE_WEBSOCKET: string
  readonly VITE_SOCKET_URL: string
  readonly VITE_UPLOAD_URL: string
  readonly VITE_CDN_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 全局类型声明
declare global {
  interface Window {
    __AI_SCHOOL_CONFIG__: {
      apiBaseUrl: string
      appTitle: string
      version: string
    }
  }
}

export {}