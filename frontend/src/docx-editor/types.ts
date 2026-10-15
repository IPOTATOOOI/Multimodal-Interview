import { DocumentActionEnum } from "@/docx-editor/enum"

export type PageModeType = "A3" | "A4"

export type DocumentActionType = keyof typeof DocumentActionEnum

export interface DocxDocumentItem {
  _id?: string
  title: string
  type: "word"
  content: string | Record<string, any>
  pageMode: PageModeType
  updateTime: number
  createdTime: number
  creator?: string
}

export interface DocumentItem {
  _id?: string
  title: string
  type: string
  updateTime?: number
  createdTime?: number
}

export interface BaseOption {
  label: string
  value: string | number
}
