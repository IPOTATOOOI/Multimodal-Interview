<template>
  <div class="side-toolbar-root">
    <div v-if="!documentStore.editable" class="side-tool-bar-item">
      <SearchPopover :editor="editor" style="margin-left: 400px" :just-icon="false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
import { Editor } from "@tiptap/vue-3"
import { DocumentItem } from "@/docx-editor/types"
import useDocumentStore from "@/docx-editor/store/documentStore"
import { SearchPopover } from "@/docx-editor/editor-functions"

interface PropsType {
  editor: Editor | undefined
  nowDoc: DocumentItem
  editorHeaderRef: Record<string, any> | undefined
}

const props = withDefaults(defineProps<PropsType>(), {})

const documentStore = useDocumentStore()
</script>

<style lang="less" scoped>
.side-toolbar-root {
  width: 100%;
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
  row-gap: 10px;
  padding-top: 10px;
  box-sizing: border-box;
  border: 1px solid #eee;
  box-shadow: -5px 0 10px -5px #ddd;

  .side-tool-bar-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    font-size: 12px;
    i {
      font-size: 24px;
      padding: 5px;
      color: gray;
    }
    &:hover {
      i {
        background: rgba(0, 0, 0, 0.04);
      }
    }
  }
}
.side-drawer-container {
  position: absolute;
  right: 1px;
  top: 0px;
  bottom: 0px;
  margin: auto;
  border: none;
  z-index: 2;
  box-shadow: -5px 0 10px -5px #ddd;
  transition: width 0.5s;
  overflow: hidden;
}
</style>
