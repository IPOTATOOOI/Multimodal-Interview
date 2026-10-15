import { defineStore } from "pinia"
import { DocxDocumentItem } from "@/docx-editor/types"

export type { DocxDocumentItem }

export const useDocumentListStore = defineStore("documentListStore", {
  state: () => ({
    documentList: [] as DocxDocumentItem[]
  }),

  actions: {
    create(document: DocxDocumentItem) {
      this.documentList.push(document)
    },

    edit(document: DocxDocumentItem) {
      const index = this.documentList.findIndex(doc => doc._id === document._id)
      if (index !== -1) {
        this.documentList[index] = document
      }
    },

    delete(_id: string) {
      const index = this.documentList.findIndex(doc => doc._id === _id)
      if (index !== -1) {
        this.documentList.splice(index, 1)
      }
    },

    getDetail(_id: string) {
      return this.documentList.find(doc => doc._id === _id)
    }
  }
})
