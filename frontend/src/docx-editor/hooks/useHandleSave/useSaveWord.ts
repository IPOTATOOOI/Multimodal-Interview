import { DocumentActionEnum } from '@/docx-editor/enum'
import { DocumentActionType, DocxDocumentItem } from '@/docx-editor/types'
import { useDocumentStore, useDocumentListStore } from '@/docx-editor/store'
import { v4 as uuid } from 'uuid'
import { Ref } from 'vue'
const useSaveWord = (
  actionType: DocumentActionType,
  title: string,
  wordContent: '' | Record<string, any>,
  loading: Ref<boolean>,
  oldDoc: DocxDocumentItem | null,
  type: 'word',
  callback?: (document: DocxDocumentItem) => void,
) => {
  if (actionType !== DocumentActionEnum.Create && !oldDoc)
    throw new Error('编辑文档时，oldDoc不可为空')
  const documentStore = useDocumentStore()
  const saveTime = new Date().getTime()

  const document: DocxDocumentItem = {
    _id: oldDoc?._id || '',
    type: actionType === DocumentActionEnum.Create || !oldDoc?.type ? type : oldDoc?.type,
    title: title || '未命名文档',
    updateTime: saveTime,
    createdTime:
      actionType === DocumentActionEnum.Create || !oldDoc?.type ? saveTime : oldDoc?.createdTime,
    content: wordContent,
    creator: oldDoc?.creator || '易企签用户',
    pageMode: documentStore.pageMode,
  }

  const documentListStore = useDocumentListStore()
  loading.value = true
  if (actionType === DocumentActionEnum.Create) {
    const id = uuid()
    document._id = id
    documentListStore.create(document)
  } else {
    documentListStore.edit(document)
  }
  documentStore.$patch({ isSave: true })
  loading.value = false
  callback && callback(document)
}

export default useSaveWord
