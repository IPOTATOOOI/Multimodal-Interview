<template>
  <div class="emoji-select-container">
    <el-popover ref="EmojiRef" placement="top" :width="310" trigger="click">
      <div class="emoji-list">
        <div
          v-for="(item, index) in emojiList"
          :key="index"
          class="emoji-item"
          @click="setEmoji({ emoji: item })"
        >
          {{ item }}
        </div>
      </div>
      <template #reference>
        <i class="ri-user-smile-line"></i>
      </template>
    </el-popover>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const EmojiRef = ref()

const emojiList = [
  '😀',
  '😃',
  '😄',
  '😁',
  '😆',
  '😅',
  '🤣',
  '😂',
  '🙂',
  '😊',
  '😇',
  '🥰',
  '😍',
  '🤩',
  '😘',
  '😗',
  '😚',
  '😋',
  '😛',
  '😝',
  '🤑',
  '🤗',
  '🤭',
  '🤫',
  '🤔',
  '🤐',
  '🤨',
  '😐',
  '😑',
  '😶',
  '😏',
  '😒',
  '🙄',
  '😬',
  '🤥',
  '😌',
  '😔',
  '😪',
  '🤤',
  '😴',
  '😷',
  '🤒',
  '🤕',
  '🤢',
  '🤮',
  '🥵',
  '🥶',
  '🥴',
  '😵',
  '🤯',
  '🤠',
  '🥳',
  '🥸',
  '😎',
  '🤓',
  '🧐',
  '😕',
  '😟',
  '🙁',
  '☹️',
  '😮',
  '😯',
  '😲',
  '😳',
  '🥺',
  '🥹',
  '😦',
  '😧',
  '😨',
  '😰',
  '😥',
  '😢',
  '😭',
  '😱',
  '😖',
  '😣',
  '😞',
  '😓',
  '😩',
  '😫',
  '🥱',
  '😤',
  '😡',
  '😠',
  '🤬',
  '😈',
  '👿',
  '💀',
  '☠️',
  '💩',
  '🤡',
  '👹',
  '👺',
  '👻',
  '👽',
  '👾',
  '🤖',
  '🎃',
  '😺',
  '😸',
  '😹',
  '😻',
  '😼',
  '😽',
  '🙀',
  '😿',
  '😾',
  '💋',
  '👄',
  '👅',
  '👂',
  '👃',
  '👁️',
  '👀',
  '👨',
  '👩',
  '👴',
  '👵',
  '👶',
  '👧',
  '👦',
  '👩',
  '👨',
  '🧑',
  '👱',
  '👸',
  '🤴',
  '👲',
  '🧔',
  '👳',
  '🧕',
  '👼',
  '🤰',
  '🤱',
  '👩‍🍼',
  '👨‍🍼',
  '👨‍👩‍👧',
  '👨‍👩‍👧‍👦',
  '👨‍👩‍👦‍👦',
  '👨‍👩‍👧‍👧',
  '👩‍👩‍👧',
  '👩‍👩‍👧‍👦',
  '👩‍👩‍👦‍👦',
  '👩‍👩‍👧‍👧',
  '👨‍👨‍👧',
  '👨‍👨‍👧‍👦',
  '👨‍👨‍👦‍👦',
  '👨‍👨‍👧‍👧',
  '👨‍👦',
  '👨‍👦‍👦',
  '👨‍👧',
  '👨‍👧‍👧',
  '👩‍👦',
  '👩‍👦‍👦',
  '👩‍👧',
  '👩‍👧‍👧',
  '👪',
  '👨‍👩‍👧',
  '👨‍👩‍👦',
  '🏃',
  '🏃‍♀️',
  '🏃‍♂️',
  '🚶',
  '🚶‍♀️',
  '🚶‍♂️',
  '👫',
  '👭',
  '👬',
  '💑',
  '👩‍❤️‍👩',
  '👨‍❤️‍👨',
  '👩‍❤️‍💋‍👩',
  '👨‍❤️‍💋‍👨',
  '💏',
  '👪',
  '👨‍👩‍👧‍👦',
]

const emits = defineEmits(['addEmoji'])
function setEmoji(emoji) {
  emits('addEmoji', emoji)
  EmojiRef.value?.hide()
}
</script>

<style lang="less" scoped>
.emoji-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  .emoji-item {
    width: 20px;
    height: 20px;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 5px;
    &:hover {
      background: rgba(0, 0, 0, 0.1);
    }
  }
}
</style>
