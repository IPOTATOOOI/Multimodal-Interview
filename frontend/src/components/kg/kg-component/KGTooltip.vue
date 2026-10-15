<template>
  <div
    class="kg-tooltip"
    :style="{
      left: position.x + 'px',
      top: position.y + 'px',
      display: visible ? 'block' : 'none',
    }"
  >
    <div class="tooltip-title">{{ data.name }}</div>
    <div v-if="data.type" class="tooltip-content">
      <div class="tooltip-item">
        <span class="label">类型:</span>
        <span class="value">{{ data.type }}</span>
      </div>
      <div
        v-for="(value, key) in data.properties"
        v-show="key != 'embedding' && key != 'fastrp_embedding'"
        :key="key"
        class="tooltip-item"
      >
        <span class="label">{{ key }}:</span>
        <span class="value">{{ value }}</span>
      </div>
    </div>
    <div v-if="data.relation" class="tooltip-content">
      <div class="tooltip-item">
        <span class="label">关系类型:</span>
        <span class="value">{{ data.name }}</span>
      </div>
      <div class="tooltip-item">
        <span class="label">来源:</span>
        <span class="value">{{ data.source.name }}</span>
      </div>
      <div class="tooltip-item">
        <span class="label">目标:</span>
        <span class="value">{{ data.target.name }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'KGTooltip',
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    position: {
      type: Object,
      default: () => ({ x: 0, y: 0 }),
    },
    data: {
      type: Object,
      default: () => ({}),
    },
  },
}
</script>

<style scoped>
.kg-tooltip {
  position: fixed;
  background: rgba(255, 255, 255, 0.75); /* 更柔和的白色背景 */
  color: #333; /* 深灰色文字，提升可读性 */
  padding: 12px;
  border-radius: 8px; /* 更圆润的圆角 */
  font-size: 13px;
  min-width: 240px;
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* 添加微妙阴影 */
  transition: opacity 0.2s ease;
  opacity: 0.95; /* 保持轻微不透明度 */
}

.tooltip-title {
  font-weight: 600;
  margin-bottom: 8px;
  font-size: 15px;
  color: #2c3e50; /* 深蓝色标题 */
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 6px; /* 增加行间距 */
}

.tooltip-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05); /* 微弱分割线 */
}

.label {
  color: #7f8c8d; /* 柔和的灰色标签 */
  font-weight: 500;
  width: 45%; /* 保持标签宽度一致 */
  text-align: right;
  padding-right: 5px;
}

.value {
  color: #2c3e50; /* 主要文字颜色 */
  font-weight: 500;
  width: 55%;
  text-align: left;
}

/* 优化关系类型显示 */
.tooltip-content:last-child {
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding-top: 6px;
}
</style>
