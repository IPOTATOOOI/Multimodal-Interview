<template>
  <div class="kg-toolbar">
    <!-- 节点类型选择 -->
    <div class="toolbar-section">
      <div class="section-header">
        <Icon icon="lucide:circle" class="w-4 h-4" />
        <span>节点类型</span>
      </div>
      <div class="button-group">
        <button
          class="filter-btn"
          :class="{ active: selectedNodeType === '' }"
          @click="selectNodeType('')"
        >
          全部
        </button>
        <button
          v-for="type in nodeTypes"
          :key="type"
          class="filter-btn node-filter-btn"
          :class="{ active: selectedNodeType === type }"
          @click="selectNodeType(type)"
        >
          {{ type }}
        </button>
      </div>
    </div>

    <!-- 关系类型选择 -->
    <div class="toolbar-section">
      <div class="section-header">
        <Icon icon="lucide:link" class="w-4 h-4" />
        <span>关系类型</span>
      </div>
      <div class="button-group">
        <button
          class="filter-btn"
          :class="{ active: selectedLinkType === '' }"
          @click="selectLinkType('')"
        >
          全部
        </button>
        <button
          v-for="type in linkTypes"
          :key="type"
          class="filter-btn link-filter-btn"
          :class="{ active: selectedLinkType === type }"
          @click="selectLinkType(type)"
        >
          {{ type }}
        </button>
      </div>
    </div>

    <!-- 搜索功能 -->
    <div class="toolbar-section">
      <div class="section-header">
        <Icon icon="lucide:search" class="w-4 h-4" />
        <span>搜索节点</span>
      </div>
      <div class="search-container">
        <input
          type="text"
          v-model="searchText"
          placeholder="输入节点名称..."
          @input="onSearchChange"
          class="search-input"
        />
        <Icon icon="lucide:search" class="search-icon" />
      </div>
    </div>

    <!-- 节点数量控制 -->
    <div class="toolbar-section">
      <div class="section-header">
        <Icon icon="lucide:sliders-horizontal" class="w-4 h-4" />
        <span>节点数量</span>
      </div>
      <div class="number-input-container">
        <input
          type="number"
          v-model.number="nodeCount"
          min="1"
          @change="onNodeCountChange"
          class="number-input"
        />
        <div class="number-controls">
          <button @click="decreaseNodeCount" class="number-btn">-</button>
          <button @click="increaseNodeCount" class="number-btn">+</button>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="toolbar-section">
      <div class="action-buttons">
        <button class="action-btn primary" @click="onReset">
          <Icon icon="lucide:refresh-cw" class="w-4 h-4" />
          重置
        </button>
      </div>
    </div>

    <!-- 删除操作区域 -->
    <div class="toolbar-section delete-section" v-if="hasSelection">
      <div class="section-header">
        <Icon icon="lucide:trash-2" class="w-4 h-4" />
        <span>删除操作</span>
      </div>
      <div class="selection-info">
        <span class="selection-count">已选节点: {{ selectedNodesCount }}</span>
      </div>
      <div class="delete-buttons">
        <button
          class="action-btn danger"
          @click="onDeleteNodes"
          :disabled="selectedNodesCount === 0 || isDeleting"
        >
          <Icon icon="lucide:trash-2" class="w-4 h-4" />
          删除节点
        </button>
        <button
          class="action-btn secondary"
          @click="onClearSelection"
          :disabled="isDeleting"
        >
          <Icon icon="lucide:x" class="w-4 h-4" />
          清空选择
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { Icon } from '@iconify/vue'

export default {
  name: 'KGToolbar',
  components: {
    Icon,
  },
  props: {
    // 初始节点数量
    initialNodeCount: {
      type: Number,
      default: 50,
    },
    // 所有可用节点类型
    nodeTypes: {
      type: Array,
      default: () => [],
    },
    // 所有可用关系类型
    linkTypes: {
      type: Array,
      default: () => [],
    },
    // 选中的节点数量
    selectedNodesCount: {
      type: Number,
      default: 0,
    },
    // 是否正在删除
    isDeleting: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      selectedNodeType: '',
      selectedLinkType: '',
      searchText: '',
      nodeCount: this.initialNodeCount,
    }
  },
  computed: {
    hasSelection() {
      return this.selectedNodesCount > 0
    },
  },
  methods: {
    // 选择节点类型
    selectNodeType(type) {
      this.selectedNodeType = type
      // 清空其他筛选条件
      this.selectedLinkType = ''
      this.searchText = ''

      // 通知父组件筛选条件变化
      this.$emit('filter-change', {
        type: 'nodeType',
        value: type,
      })
    },

    // 选择关系类型
    selectLinkType(type) {
      this.selectedLinkType = type
      // 清空其他筛选条件
      this.selectedNodeType = ''
      this.searchText = ''

      // 通知父组件筛选条件变化
      this.$emit('filter-change', {
        type: 'linkType',
        value: type,
      })
    },

    onSearchChange() {
      // 清空其他筛选条件
      this.selectedNodeType = ''
      this.selectedLinkType = ''

      // 通知父组件筛选条件变化
      this.$emit('filter-change', {
        type: 'search',
        value: this.searchText,
      })
    },

    onNodeCountChange() {
      // 通知父组件节点数量变化
      this.$emit('node-count-change', this.nodeCount)

      // 清空其他筛选条件
      this.selectedNodeType = ''
      this.selectedLinkType = ''
      this.searchText = ''
    },

    // 增加节点数量
    increaseNodeCount() {
      this.nodeCount += 1
      this.onNodeCountChange()
    },

    // 减少节点数量
    decreaseNodeCount() {
      if (this.nodeCount > 1) {
        this.nodeCount -= 1
        this.onNodeCountChange()
      }
    },

    onReset() {
      // 重置所有筛选条件
      this.selectedNodeType = ''
      this.selectedLinkType = ''
      this.searchText = ''
      this.nodeCount = this.initialNodeCount

      // 通知父组件重置
      this.$emit('reset')
    },

    // 更新节点计数（由父组件调用）
    updateNodeCount(count) {
      this.nodeCount = count
    },

    // 删除选中的节点
    onDeleteNodes() {
      this.$emit('delete-nodes')
    },

    // 清空选择
    onClearSelection() {
      this.$emit('clear-selection')
    },
  },
}
</script>

<style scoped>
.kg-toolbar {
  height: 100%;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow-y: auto;
}

/* 自定义滚动条 */
.kg-toolbar::-webkit-scrollbar {
  width: 6px;
}

.kg-toolbar::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.kg-toolbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.kg-toolbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}


/* 工具栏区域 */
.toolbar-section {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.toolbar-section:last-child {
  border-bottom: none;
}

/* 区域标题 */
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.section-header i {
  color: #6366f1;
  font-size: 16px;
}

/* 按钮组 */
.button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: #ffffff;
  color: #64748b;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.filter-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  box-shadow: 0 4px 8px rgba(99, 102, 241, 0.2);
}

.filter-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.node-filter-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.link-filter-btn.active {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* 搜索容器 */
.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 40px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 14px;
}

/* 数字输入容器 */
.number-input-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.number-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 14px;
  background: #f8fafc;
  transition: all 0.2s ease;
}

.number-input:focus {
  outline: none;
  border-color: #6366f1;
  background: white;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.number-controls {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.number-btn {
  width: 24px;
  height: 24px;
  border: 2px solid #e2e8f0;
  background: white;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.number-btn:hover {
  border-color: #6366f1;
  color: #6366f1;
  background: #f0f4ff;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.primary {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.action-btn.primary:hover:not(:disabled) {
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.action-btn.danger {
  background: linear-gradient(135deg, #ef4444 0%, #f97316 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.action-btn.danger:hover:not(:disabled) {
  box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4);
}

.action-btn.secondary {
  background: #f1f5f9;
  color: #64748b;
  border: 2px solid #e2e8f0;
}

.action-btn.secondary:hover:not(:disabled) {
  background: #e2e8f0;
  color: #374151;
}

/* 删除操作区域 */
.delete-section {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
}

.delete-section .section-header {
  color: #dc2626;
}

.delete-section .section-header i {
  color: #ef4444;
}

.selection-info {
  margin-bottom: 16px;
}

.selection-count {
  font-size: 13px;
  color: #dc2626;
  font-weight: 600;
  background: #fee2e2;
  padding: 6px 12px;
  border-radius: 8px;
  display: inline-block;
}

.delete-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 暗黑模式样式 */
.dark .kg-toolbar {
  background: #1e293b;
}

.dark .kg-toolbar::-webkit-scrollbar-track {
  background: #334155;
}

.dark .kg-toolbar::-webkit-scrollbar-thumb {
  background: #475569;
}

.dark .kg-toolbar::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}


.dark .toolbar-section {
  border-bottom-color: #334155;
}

.dark .section-header {
  color: #e2e8f0;
}

.dark .section-header i {
  color: #8b5cf6;
}

.dark .filter-btn {
  background: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

.dark .filter-btn:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
}

.dark .filter-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.dark .node-filter-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.dark .link-filter-btn.active {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.dark .search-input {
  background: #334155;
  border-color: #475569;
  color: #e2e8f0;
}

.dark .search-input:focus {
  border-color: #8b5cf6;
  background: #1e293b;
}

.dark .search-icon {
  color: #64748b;
}

.dark .number-input {
  background: #334155;
  border-color: #475569;
  color: #e2e8f0;
}

.dark .number-input:focus {
  border-color: #8b5cf6;
  background: #1e293b;
}

.dark .number-btn {
  background: #334155;
  border-color: #475569;
  color: #cbd5e1;
}

.dark .number-btn:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
  background: #1e293b;
}

.dark .action-btn.primary {
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
}

.dark .action-btn.secondary {
  background: #334155;
  color: #cbd5e1;
  border-color: #475569;
}

.dark .action-btn.secondary:hover:not(:disabled) {
  background: #475569;
  color: #e2e8f0;
}

.dark .delete-section {
  background: #2d1b1b;
  border-left-color: #ef4444;
}

.dark .delete-section .section-header {
  color: #fca5a5;
}

.dark .delete-section .section-header i {
  color: #ef4444;
}

.dark .selection-count {
  background: #7f1d1d;
  color: #fca5a5;
}
</style>
