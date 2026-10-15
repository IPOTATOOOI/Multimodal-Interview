declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'crypto-js';

declare module '@xfyun/rtc-player' {
  export class RTCPlayer {
    constructor()
    on(event: string, callback: (e?: any) => void): RTCPlayer
    play(): void
    resume(): void
    destroy(): void
    playerType: number
    stream: any
    videoSize: { width: number; height: number }
    container: HTMLElement
  }
}

declare module '../rtcplayer.esm.js' {
  export class RTCPlayer {
    constructor()
    on(event: string, callback: (e?: any) => void): RTCPlayer
    play(): void
    resume(): void
    destroy(): void
    playerType: number
    stream: any
    videoSize: { width: number; height: number }
    container: HTMLElement
  }
}

declare module '*.js' {
  const content: any
  export default content
  export const RTCPlayer: any
}
