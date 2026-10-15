import { DocumentActionEnum } from '@/docx-editor/enum'
import { useDocumentStore, useDocumentListStore } from '@/docx-editor/store'
import { Ref } from 'vue'
import { v4 as uuid } from 'uuid'
const useSaveCommon = (
  actionType: string,
  type: string,
  title: string,
  content: any,
  loading: Ref<boolean>,
  oldDocument: any | null,
  callback?: (document: Record<string, any>) => void,
) => {
  if (actionType !== DocumentActionEnum.Create && !oldDocument)
    throw new Error('编辑时，oldDocument不可为空')

  const documentStore = useDocumentStore()

  const saveTime = new Date().getTime()

  const document: Record<string, any> = {
    _id: oldDocument?._id || '',
    type: type,
    title: title || '未命名',
    updateTime: saveTime,
    createdTime:
      actionType === DocumentActionEnum.Create || !oldDocument ? saveTime : oldDocument.createdTime,
    creator: '易企签用户',
    content: content,
    commentList:
      actionType === DocumentActionEnum.Create || !oldDocument ? [] : oldDocument.commentList,
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

export default useSaveCommon
