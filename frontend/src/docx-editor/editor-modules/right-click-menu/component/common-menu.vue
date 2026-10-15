<template>
  <div class="menu-container common-menu">
    <ContextMenuItem @click="copyData">
      <div>复制</div>
      <template #shortcut><div>Ctrl + C</div></template>
    </ContextMenuItem>

    <ContextMenuItem @click="cutData">
      <div>剪切</div>
      <template #shortcut><div>Ctrl + X</div></template>
    </ContextMenuItem>

    <ContextMenuItem @click="pastData">
      <div>粘贴</div>
      <template #shortcut><div>Ctrl + V</div></template>
    </ContextMenuItem>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue"
import { Editor } from "@tiptap/vue-3"
import { useClipboard } from "@vueuse/core"
import { ContextMenuItem } from "@/docx-editor/components/index"

const props = defineProps<{
  editor: Editor | undefined
}>()

let cursorTxt = ""

// 复制
function copyData() {
  const { copy } = useClipboard({})
  copy(cursorTxt)
}

// 粘贴
function pastData() {
  props.editor?.commands.insertContent(cursorTxt)
}

// 剪切
function cutData() {
  props.editor?.commands.deleteSelection()
}

onMounted(() => {
  setTimeout(() => {
    if (props.editor)
      props.editor.on("selectionUpdate", editor => {
        updateSelectedText(editor)
      })
  })
})

// 选中的文本
function updateSelectedText(editor) {
  const selection = window.getSelection()
  if (selection?.toString()) {
    cursorTxt = selection.toString()
  }
}
</script>

<style lang="less" scoped>
.common-menu {
  display: flex;
  flex-direction: column;
}
</style>
