declare module 'markdown-it' {
  export type MarkdownItPlugin<T = unknown> = (md: MarkdownIt, options?: T) => void

  export default class MarkdownIt {
    constructor(options?: Record<string, unknown>)
    use<T = unknown>(plugin: MarkdownItPlugin<T>, options?: T): this
    render(src: string): string
  }
}
