<template>
  <div class="kg-container">
    <!-- 左侧工具栏 -->
    <div class="kg-sidebar">
      <KGToolbar
        ref="toolbar"
        :initial-node-count="initialNodeCount"
        :node-types="allNodeTypes"
        :link-types="allLinkTypes"
        :selected-nodes-count="selectedNodes.size"
        :is-deleting="isDeleting"
        @filter-change="handleFilterChange"
        @reset="handleReset"
        @node-count-change="handleNodeCountChange"
        @delete-nodes="deleteSelectedNodes"
        @clear-selection="clearSelection"
      />
    </div>

    <!-- 右侧画布区域 -->
    <div class="kg-canvas-area">
      <div class="canvas-container">
        <KGTooltip :visible="tooltipVisible" :position="tooltipPosition" :data="tooltipData" />

        <!-- 添加加载状态提示 -->
        <div
          v-if="loading"
          class="loading-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in"
        >
          <div class="flex flex-col items-center mb-20">
            <div
              class="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"
            ></div>
            <div class="loading-text text-white text-lg font-medium animate-pulse">
              加载图数据中...
            </div>
          </div>
        </div>

        <!-- 错误提示带动画 -->
        <div
          v-if="error"
          class="error-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50 animate-fade-in"
        >
          <div
            class="bg-white rounded-lg p-6 max-w-md w-full shadow-2xl transform transition-all animate-slide-up"
          >
            <div class="error-icon text-red-500 text-4xl mb-4 flex justify-center">
              <i class="fas fa-exclamation-circle animate-shake"></i>
            </div>
            <div class="error-text text-gray-800 text-center mb-6 text-lg">{{ error }}</div>
            <button
              class="retry-button bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-full transition-all transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 w-full"
            >
              重试
            </button>
          </div>
        </div>

        <slot></slot>
        <i class="el-icon-download" @click="downLoadGraph"></i>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3'
import { saveSvgAsPng } from 'save-svg-as-png'
import KGToolbar from './KGToolbar.vue'
import KGTooltip from './KGTooltip.vue'
import { getApiUrl } from '@/config/api'

export default {
  name: 'cvs',
  components: {
    KGToolbar,
    KGTooltip,
  },
  data() {
    return {
      //用于更新画布
      nodes: [],
      links: [],
      nodeText: [],
      linksName: [],
      simulation: null,
      width: 800,
      height: 600,
      //用于判断是更新还是初始化
      initialized: false,
      nodeSizeList: new Map(), //类型与半径的对应关系
      nodeTextLengthList: new Map(), //类型与节点文本个数的对应关系
      scale: d3.scaleOrdinal(d3.schemeCategory10), //用于随机展示节点颜色
      typeColors: {
        person: '#FF6B6B', // 人物节点颜色
        dynasty: '#4ECDC4', // 朝代节点颜色
        title: '#45B7D1', // 称号节点颜色
        location: '#96CEB4', // 地点节点颜色
      },

      initialNodeCount: 5, // 初始节点数量
      fullData: null, // 存储完整数据
      filteredData: null, // 存储筛选后的数据
      tooltipVisible: false,
      tooltipPosition: { x: 0, y: 0 },
      tooltipData: {},

      allNodeTypes: [], // 存储所有节点类型
      allLinkTypes: [], // 存储所有关系类型
      loading: false, // 加载状态
      error: '', // 错误信息

      // 选中状态管理
      selectedNodes: new Set(), // 选中的节点ID集合
      isDeleting: false, // 删除操作状态
    }
  },
  mounted() {
    // 设置节点大小
    this.nodeSizeList.set('person', 40)
    this.nodeSizeList.set('dynasty', 50)
    this.nodeSizeList.set('title', 35)
    this.nodeSizeList.set('location', 38)
    this.nodeSizeList.set('Question', 42)
    this.nodeSizeList.set('User', 38)

    // 设置文本长度
    this.nodeTextLengthList.set('person', 4)
    this.nodeTextLengthList.set('dynasty', 4)
    this.nodeTextLengthList.set('title', 3)
    this.nodeTextLengthList.set('location', 4)

    // 初始只显示部分节点
    // this.limitInitialNodes()
    // this.renderGraph(this.filteredData)
    this.fetchGraphData()
  },

  methods: {
    // 从FastAPI后端获取图数据
    async fetchGraphData() {
      this.loading = true
      this.error = ''

      try {
        // 获取用户ID和角色信息
        const userId = localStorage.getItem('user_id')
        const isAdmin = localStorage.getItem('userRole') === 'admin'

        if (!userId) {
          throw new Error('未获取到用户ID，请重新登录')
        }

        // 构建请求URL，添加user_id和is_admin参数
        const url = new URL(getApiUrl('/graph/data'))
        url.searchParams.append('user_id', userId)
        url.searchParams.append('is_admin', isAdmin.toString())

        console.log('请求图谱数据URL:', url.toString())
        const response = await fetch(url.toString())
        console.log(response)
        if (!response.ok) {
          throw new Error(`获取数据失败: HTTP ${response.status}`)
        }

        const data = await response.json()
        console.log('获取到的图数据:', data)

        // ----------- 唯一ID修正逻辑开始 -----------
        // 过滤掉无效的节点（null 或 undefined）
        const validNodes = (data.nodes || []).filter((node) => node != null)
        // 过滤掉无效的链接（null 或 source/target 为 null）
        const validLinks = (data.links || []).filter((link) => {
          return link && link.source != null && link.target != null
        })

        // 为节点生成唯一ID
        const nodeIdMap = new Map()
        const nodes = validNodes.map((node, idx) => {
          // 处理节点ID：如果节点ID不存在，则用name+type生成
          const idPrefix = node.id ? node.id : `${node.name || 'node'}_${node.type || 'unknown'}`
          const newId = `${idPrefix}_${idx}`
          nodeIdMap.set(node.id, newId)
          return { ...node, id: newId }
        })

        // 处理链接
        const links = validLinks.map((link) => {
          // 处理source和target的ID
          const getSourceId = (source) => {
            if (typeof source === 'object' && source.id != null) return source.id
            return source
          }

          const getTargetId = (target) => {
            if (typeof target === 'object' && target.id != null) return target.id
            return target
          }

          const sourceId = getSourceId(link.source)
          const targetId = getTargetId(link.target)

          // 映射到新ID
          const newSource = nodeIdMap.get(sourceId) || sourceId
          const newTarget = nodeIdMap.get(targetId) || targetId

          return {
            ...link,
            source: newSource,
            target: newTarget,
          }
        })

        this.fullData = { nodes, links }
        // ----------- 唯一ID修正逻辑结束 -----------

        // 提取所有节点类型和关系类型
        this.extractAllTypes()

        // 初始只显示部分节点
        this.limitInitialNodes()
        this.renderGraph(this.filteredData)
      } catch (err) {
        console.error('获取图数据失败:', err)
        this.error = `获取数据失败: ${err.message || '未知错误'}`

        this.fullData = { nodes: [], links: [] }
        this.filteredData = this.fullData
        this.extractAllTypes()
        this.renderGraph(this.filteredData)
      } finally {
        this.loading = false
      }
    },

    // 提取所有节点类型和关系类型
    extractAllTypes() {
      // 提取所有节点类型
      const nodeTypesSet = new Set()
      this.fullData.nodes.forEach((node) => {
        if (node.type) {
          nodeTypesSet.add(node.type)
        }
      })
      this.allNodeTypes = Array.from(nodeTypesSet)

      // 提取所有关系类型
      const linkTypesSet = new Set()
      this.fullData.links.forEach((link) => {
        if (link.name) {
          linkTypesSet.add(link.name)
        }
      })
      this.allLinkTypes = Array.from(linkTypesSet)

      console.log('提取的节点类型:', this.allNodeTypes)
      console.log('提取的关系类型:', this.allLinkTypes)
    },

    // 新增辅助方法
    resetBeforeFilter() {
      // 停止之前的模拟
      if (this.simulation) {
        this.simulation.stop()
      }

      // 清除原有SVG
      d3.select('.canvas-container').select('svg').remove()

      // 重置初始化状态
      this.initialized = false

      // 重置过滤数据到初始状态
      this.filteredData = JSON.parse(JSON.stringify(this.fullData))
    },

    // 限制初始节点数量的方法 - 已移到methods内部
    limitInitialNodes() {
      // 确保使用最新的完整数据进行筛选
      const limitedNodes = this.fullData.nodes.slice(0, this.initialNodeCount)
      const limitedNodeIds = new Set(limitedNodes.map((node) => node.id))

      const limitedLinks = this.fullData.links.filter((link) => {
        const sourceId =
          link.source && typeof link.source === 'object' ? link.source.id : link.source
        const targetId =
          link.target && typeof link.target === 'object' ? link.target.id : link.target
        return limitedNodeIds.has(sourceId) && limitedNodeIds.has(targetId)
      })

      this.filteredData = {
        nodes: limitedNodes,
        links: limitedLinks,
      }

      if (this.$refs.toolbar) {
        this.$refs.toolbar.updateNodeCount(limitedNodes.length)
      }
    },

    // 处理筛选变化
    handleFilterChange(filter) {
      // 每次筛选前先重置
      this.resetBeforeFilter()

      let filteredNodes = []
      let filteredLinks = []

      if (filter.type === 'nodeType' && filter.value) {
        // 按节点类型筛选
        filteredNodes = this.fullData.nodes.filter((node) => node.type === filter.value)
        const filteredNodeIds = new Set(filteredNodes.map((node) => node.id))

        filteredLinks = this.fullData.links.filter(
          (link) =>
            filteredNodeIds.has(link.source.id || link.source) &&
            filteredNodeIds.has(link.target.id || link.target),
        )
      } else if (filter.type === 'linkType' && filter.value) {
        // 按关系类型筛选
        filteredLinks = this.fullData.links.filter((link) => link.name === filter.value)
        const relatedNodeIds = new Set()
        filteredLinks.forEach((link) => {
          relatedNodeIds.add(link.source.id || link.source)
          relatedNodeIds.add(link.target.id || link.target)
        })
        filteredNodes = this.fullData.nodes.filter((node) => relatedNodeIds.has(node.id))
      } else if (filter.type === 'search' && filter.value) {
        const searchTerm = filter.value.toLowerCase()

        // 1. 找到搜索匹配的节点
        const searchedNodes = this.fullData.nodes.filter(
          (node) => node.name && node.name.toLowerCase().includes(searchTerm),
        )

        if (searchedNodes.length === 0) {
          return
        }

        const searchedNodeIds = new Set(searchedNodes.map((node) => node.id))

        // 2. 找出与搜索节点直接相连的边
        const directLinks = this.fullData.links.filter((link) => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source
          const targetId = typeof link.target === 'object' ? link.target.id : link.target
          return searchedNodeIds.has(sourceId) || searchedNodeIds.has(targetId)
        })

        // 3. 获取直接相连节点的ID
        const directNeighborIds = new Set()
        directLinks.forEach((link) => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source
          const targetId = typeof link.target === 'object' ? link.target.id : link.target
          if (searchedNodeIds.has(sourceId)) {
            directNeighborIds.add(targetId)
          }
          if (searchedNodeIds.has(targetId)) {
            directNeighborIds.add(sourceId)
          }
        })

        // 4. 获取所有需要显示的节点
        filteredNodes = this.fullData.nodes.filter(
          (node) => searchedNodeIds.has(node.id) || directNeighborIds.has(node.id),
        )

        // 5. 构建这些节点之间的连线
        filteredLinks = directLinks
      } else {
        // 无筛选条件时显示初始状态
        this.limitInitialNodes()
        this.renderGraph(this.filteredData)
        return
      }

      this.filteredData = {
        nodes: filteredNodes,
        links: filteredLinks,
      }

      // 更新工具栏中的节点计数
      this.$refs.toolbar.updateNodeCount(filteredNodes.length)

      // 重新渲染图谱
      this.renderGraph(this.filteredData)
    },

    // 处理重置
    handleReset() {
      // 1. 重置筛选条件
      this.filteredData = JSON.parse(JSON.stringify(this.fullData))

      // 2. 限制初始节点数量
      this.limitInitialNodes()

      // 3. 重新渲染图谱
      this.simulation.stop() // 停止之前的力导向模拟
      this.initialized = false // 重置初始化状态

      // 4. 清除原有的SVG元素
      d3.select('.canvas-container').select('svg').remove()

      // 5. 重新初始化图谱
      this.renderGraph(this.filteredData)
    },
    handleNodeCountChange(newCount) {
      this.initialNodeCount = newCount

      // 重新筛选节点
      const limitedNodes = this.fullData.nodes.slice(0, newCount)
      const limitedNodeIds = new Set(limitedNodes.map((node) => node.id))

      // 筛选相关的边
      const limitedLinks = this.fullData.links.filter(
        (link) =>
          limitedNodeIds.has(link.source.id || link.source) &&
          limitedNodeIds.has(link.target.id || link.target),
      )

      this.filteredData = {
        nodes: limitedNodes,
        links: limitedLinks,
      }

      // 停止之前的模拟
      if (this.simulation) {
        this.simulation.stop()
      }

      // 清除原有SVG
      d3.select('.canvas-container').select('svg').remove()

      // 重置初始化状态
      this.initialized = false

      // 重新渲染图谱
      this.renderGraph(this.filteredData)
    },
    renderGraph(data) {
      if (this.initialized) {
        this.updategraph(data)
      } else {
        this.initGraph(data)
        this.initialized = true
      }
    },
    initGraph(data) {
      console.log('初始化画布...', data)
      let self = this
      //将json转化为对象
      const links = data.links //.map(d => Object.create(d));
      const nodes = data.nodes //.map(d => Object.create(d));
      // console.log("nodes", nodes);
      //初始化力导向
      self.simulation = d3
        .forceSimulation(nodes)
        .force(
          'link',
          d3
            .forceLink(links)
            .id((d) => d.id)
            .distance(100), //连线的长度
        )
        .force('charge', d3.forceManyBody().strength(-1000).distanceMin(10).distanceMax(800)) //以电荷的方式 开始的力
        //设置碰撞半径 就是两个节点最近的距离
        .force('collision', d3.forceCollide(1).strength(0.1))
        .force('center', d3.forceCenter(self.width / 2, self.height / 2)) //力导向图的中心位置
      //创造容器
      //const svg = d3.create("svg").attr("viewBox", [0, 0, width, height]);
      const svg = d3
        .select('.canvas-container')
        .append('svg')
        .attr('viewBox', [0, 0, self.width, self.height])
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('preserveAspectRatio', 'xMidYMid meet')

      //设置一个背景层，对这个背景层缩放效果好
      const bg = svg.append('g')

      //为了解决因方向改变而导致的箭头位置问题设置两个箭头样式
      //思路就是双箭头，分别指向source节点和target节点，然后根据方向的不同控制不同箭头的显示
      svg
        .append('marker') //让连线和箭头关联
        .attr('id', 'positiveMarker')
        .attr('orient', 'auto')
        .attr('stroke-width', 2)
        .attr('markerUnits', 'strokeWidth')
        .attr('markerUnits', 'userSpaceOnUse')
        .attr('viewBox', '0 -5 10 10') //箭头所在的合适范围
        //refX 标记位置在路径开始处的点
        .attr('refX', 11) //箭头在方向上的偏移 让箭头露出
        .attr('refY', 0) //离左右连线偏移
        .attr('markerWidth', 12)
        .attr('markerHeight', 12)
        .append('path') //增加路径类型标签 注意不是属性
        .attr('d', 'M 0 -5 L 10 0 L 0 5') //设置路径
        .attr('fill', '#999') //填充和不可见度
        .attr('stroke-opacity', 0.6)

      svg
        .append('marker') //让连线和箭头关联
        .attr('id', 'negativeMarker')
        .attr('orient', 'auto')
        .attr('stroke-width', 2)
        .attr('markerUnits', 'strokeWidth')
        .attr('markerUnits', 'userSpaceOnUse')
        .attr('viewBox', '0 -5 10 10') //箭头所在的合适范围
        .attr('refX', 0) //箭头在方向上的偏移 让箭头露出
        .attr('refY', 0) //离左右连线偏移
        .attr('markerWidth', 12)
        .attr('markerHeight', 12)
        .append('path') //增加路径类型标签 注意不是属性
        .attr('d', 'M 0 0 L 10 5 L 10 -5') //设置路径
        .attr('fill', '#999') //填充和不可见度
        .attr('stroke-opacity', 0.6)

      //绑定缩放事件
      svg
        .call(
          d3
            .zoom()
            .scaleExtent([0.1, 2]) //增加缩放范围
            .on('zoom', function (event) {
              // 添加 event 参数
              bg.attr('transform', event.transform) // 使用 event.transform
            }),
        )
        .on('dblclick.zoom', null)

      // console.log(marker);

      //构建连接线样式
      self.links = bg
        .append('g')
        .selectAll('path')
        .data(links)
        .join('path')
        .attr('class', 'link')
        .attr('id', function (d) {
          if (typeof d.source === 'object') {
            return d.source.id + '_' + d.name + '_' + d.target.id
          } else {
            return d.source + '_' + d.name + '_' + d.target
          }
        })
        .on('mouseover', (event, d) => {
          this.tooltipVisible = true
          this.tooltipPosition = { x: event.pageX + 10, y: event.pageY + 10 }
          this.tooltipData = { ...d, relation: true }
        })
        .on('mouseout', () => {
          this.tooltipVisible = false
        })

      //构建连接线的文本层
      self.linksName = bg
        .append('g')
        .selectAll('text')
        .data(links)
        .join('text')
        .attr('class', 'linksName')
        .append('textPath')
        .attr('xlink:href', function (d) {
          //因为更新后d.source会变为一个对象，所以判断是否是对象然后取对象的id作为目标链接
          if (typeof d.source === 'object') {
            return '#' + d.source.id + '_' + d.name + '_' + d.target.id
          } else {
            return '#' + d.source + '_' + d.name + '_' + d.target
          }
        })
        .attr('startOffset', '50%') //属性名写错导致不会生效
        .text(function (d) {
          return d.name
        })
      //构建节点样式
      self.nodes = bg
        .append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('class', 'node')
        .attr('r', 32.5)
        .attr('fill', self.color())
        .on('dblclick', self.queryProp)
        .on('click', (event, d) => {
          // 支持Ctrl键多选
          if (event.ctrlKey || event.metaKey) {
            self.toggleNodeSelection(d.id)
          } else {
            // 单选模式：清空其他选中项，只选中当前项
            self.clearSelection()
            self.toggleNodeSelection(d.id)
          }
          self.queryTest(d)
        })
        .on('mouseover', (event, d) => {
          this.tooltipVisible = true
          this.tooltipPosition = { x: event.pageX + 10, y: event.pageY + 10 }
          this.tooltipData = d
        })
        .on('mouseout', () => {
          this.tooltipVisible = false
        })
        .call(self.drag(self.simulation))
      // //增加节点的名字
      // self.nodes.append('title').text((d) => d.name)

      //节点文本层
      self.nodeText = bg
        .append('g')
        .selectAll('text') //选择所有的text元素
        .data(nodes) //绑定源数据
        .join('text') //连接起来
        .text((d) => {
          if (!d) return ''
          let name = d.name
          if (d.type === 'Question' && d.properties && d.properties.title) {
            name = d.properties.title
          } else if (d.type === 'User' && d.properties) {
            name = d.id.toString()
          }
          let len = this.nodeTextLengthList.has(d.type) ? this.nodeTextLengthList.get(d.type) : 6
          if (name && name.length > len) return name.slice(0, len) + '...'
          return name || ''
        })
        .attr('dy', 2)
        .style('pointer-events', 'none')
        .attr('class', 'node-text')

      //将层与仿真关联起来
      self.simulation.on('tick', () => {
        //设置连接线的跟随
        //根据源节点与目标节点的相对关系设置 路径方向
        self.links
          .attr('d', function (d) {
            //这个是为了解决文字方向的问题
            if (d.source.x < d.target.x) {
              return (
                'M ' + self.getCoord(d.target, d.source) + ' L ' + self.getCoord(d.source, d.target)
              )
            } else {
              return (
                'M ' + self.getCoord(d.source, d.target) + ' L ' + self.getCoord(d.target, d.source)
              )
            }
          })
          //根据方向不同选择显示不同的marker
          //这是由于解决文字方向而引起的附加问题
          //对于尾端，如果是源节点指向目的节点的时候要在尾部加箭头
          .attr('marker-end', function (d) {
            if (d.source.x < d.target.x) {
              return 'url(#positiveMarker)'
            } else {
              return null
            }
          })
          .attr('marker-start', function (d) {
            if (d.source.x > d.target.x) {
              //如果源节点比目的节点大的时候，就认为是目的节点是源节点
              return 'url(#negativeMarker)'
            } else {
              return null
            }
          })

        self.nodes.attr('cx', (d) => d.x).attr('cy', (d) => d.y)
        //这个x,y是由什么决定的 是由 text的属性决定的 svg中text标签的属性
        self.nodeText.attr('x', (d) => d.x).attr('y', (d) => d.y)
      })
    },
    //给出源节点和目标节点，返回目标节点的边上距离源节点最近的点的坐标
    getCoord(source, target) {
      //根据目标节点的类型，计算路径的长度，让路径指向目标节点的边，而不是圆心

      let r = 30
      if (this.nodeSizeList.has(target.type)) {
        r = this.nodeSizeList.get(target.type)
      }
      // console.log(r);
      let scale = r / Math.sqrt(Math.pow(target.y - source.y, 2) + Math.pow(target.x - source.x, 2))

      let targetX = target.x - scale * (target.x - source.x)
      let targetY = target.y - scale * (target.y - source.y)
      return targetX + ' ' + targetY
    },
    color() {
      return (d) => this.typeColors[d.type] || this.scale(d.type)
    },
    drag(simulation) {
      // 保存 d3.event 的引用
      const drag = d3.drag()

      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      }

      function dragged(event, d) {
        d.fx = event.x // 使用 event.x 而不是 d3.event.x
        d.fy = event.y // 使用 event.y 而不是 d3.event.y
      }

      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0)
        d.fx = null
        d.fy = null
      }

      return drag.on('start', dragstarted).on('drag', dragged).on('end', dragended)
    },
    queryTest(d) {
      //直接获得点击节点及其数据
      this.$emit('clickNode', d)
    },
    //查询属性
    queryProp(d) {
      this.$emit('dbclickNode', d)
    },
    updategraph(data) {
      console.log('更新图谱数据...', data)
      let self = this
      //解决重复点击线条残留问题
      const links = data.links
      const nodes = data.nodes

      //更新连线
      self.links = self.links
        .data(links, function (d) {
          if (typeof d.source === 'object') {
            return d.source.id + '_' + d.name + '_' + d.target.id
          } else {
            return d.source + '_' + d.name + '_' + d.target
          }
        })
        .join('path') //设置对象
        .merge(self.links)
        .attr('class', 'link')
        .attr('id', function (d) {
          //为了解决再次点击之后 source变为节点而导致的获取不到id的情况
          if (typeof d.source === 'object') {
            return d.source.id + '_' + d.name + '_' + d.target.id
          } else {
            return d.source + '_' + d.name + '_' + d.target
          }
        })
        .on('mouseover', (event, d) => {
          this.tooltipVisible = true
          this.tooltipPosition = { x: event.pageX + 10, y: event.pageY + 10 }
          this.tooltipData = { ...d, relation: true }
        })
        .on('mouseout', () => {
          this.tooltipVisible = false
        })
      //更新连线上的文字
      //构建连接线的文本层
      self.linksName = self.linksName
        .data(links, function (d) {
          if (typeof d.source === 'object') {
            return d.source.id + '_' + d.name + '_' + d.target.id
          } else {
            return d.source + '_' + d.name + '_' + d.target
          }
        })
        .join('text')
        .attr('class', 'linksName')
        .append('textPath')
        .attr(
          'xlink:href',
          function (d) {
            if (typeof d.source === 'object') {
              return '#' + d.source.id + '_' + d.name + '_' + d.target.id
            } else {
              return '#' + d.source + '_' + d.name + '_' + d.target
            }
          },
          // d => "#" + d.source + "_" + d.name + "_" + d.target
        )
        .attr('startOffset', '50%')
        .merge(self.linksName)
        .text(function (d) {
          return d.name
        })

      //更新节点
      self.nodes = self.nodes
        .data(nodes)
        .join('circle') //会自动处理增加减少的节点
        .merge(self.nodes)
        .on('dblclick', self.queryProp) //双击事件获得属性
        .on('click', (event, d) => {
          // 支持Ctrl键多选
          if (event.ctrlKey || event.metaKey) {
            self.toggleNodeSelection(d.id)
          } else {
            // 单选模式：清空其他选中项，只选中当前项
            self.clearSelection()
            self.toggleNodeSelection(d.id)
          }
          self.queryTest(d)
        })
        .call(self.drag(self.simulation))
        .attr('class', 'node') //设置在前面，样式就会应用于所有节点
        .attr('r', function (d) {
          if (self.nodeSizeList.has(d.type)) {
            return self.nodeSizeList.get(d.type)
          }
          return 30
        })
        .attr('fill', self.color())
      //增加节点的名字
      self.nodes
        .text('')
        .append('title')
        .text((d) => d.name)

      //字没跟着走 ,因为文字层没更新
      //节点文本层
      self.nodeText = self.nodeText
        .data(nodes) //绑定源数据
        .join('text') //连接起来
        .merge(self.nodeText)
        .text((d) => {
          if (!d || !d.name) return ''
          let name = d.name || ''
          let len = self.nodeTextLengthList.has(d.type) ? self.nodeTextLengthList.get(d.type) : 6
          if (name.length > len) return name.slice(0, len) + '...'
          return name
        })
        .attr('dy', 2)
        .style('pointer-events', 'none')
        .attr('class', 'node-text')

      //更新力
      self.simulation.nodes(nodes)
      self.simulation
        .force('link')
        // .id(d => d.index)
        .links(links)
      self.simulation.alpha(1).restart()

      // 更新选中状态样式
      self.updateNodeSelectionStyles()
    },
    modifyNodeSize(targetLabel, sizeLevel) {
      //更新节点的大小
      const sizesList = [5, 10, 25, 32.5, 40] //存放级别对应的半径大小
      const lengthList = [0, 1, 3, 4, 7] //存放级别对应的节点文本长度
      this.nodeSizeList.set(targetLabel, sizesList[sizeLevel])
      this.nodeTextLengthList.set(targetLabel, lengthList[sizeLevel])
      // console.log(this.nodeSizeList);

      this.nodes = this.nodes.attr('r', (d) => {
        if (this.nodeSizeList.has(d.type)) {
          return this.nodeSizeList.get(d.type)
        }
        return 32.5
      })
      //根据节点的类型确定节点中要展示几个文字
      this.nodeText = this.nodeText.text((d) => {
        let name = d.name
        let len = this.nodeTextLengthList.has(d.type) ? this.nodeTextLengthList.get(d.type) : 6
        if (name.length > len) return name.slice(0, len) + '...'
        return d.name
      })
      this.simulation.alpha(1).restart()
    },
    downLoadGraph() {
      // console.log("下载图谱")
      if (!d3.select('.canvas-container').select('svg').node()) {
        this.$message({
          showClose: true,
          message: '没有要下载的图谱',
        })
        return
      }
      let date = new Date()
      let pictureName = '图谱_' + date.toLocaleString() + '.png'
      saveSvgAsPng(d3.select('.canvas-container').select('svg').node(), pictureName, {
        scale: 10,
      })
    },

    // 切换节点选中状态
    toggleNodeSelection(nodeId) {
      if (this.selectedNodes.has(nodeId)) {
        this.selectedNodes.delete(nodeId)
      } else {
        this.selectedNodes.add(nodeId)
      }
      this.updateNodeSelectionStyles()
    },

    // 更新节点选中样式
    updateNodeSelectionStyles() {
      this.nodes
        .classed('selected', (d) => this.selectedNodes.has(d.id))
        .style('stroke-width', (d) => (this.selectedNodes.has(d.id) ? '4px' : '1px'))
        .style('stroke', (d) => (this.selectedNodes.has(d.id) ? '#ff6b6b' : '#cfebfe'))
    },

    // 获取关系ID
    getLinkId(link) {
      if (typeof link.source === 'object') {
        return link.source.id + '_' + link.name + '_' + link.target.id
      } else {
        return link.source + '_' + link.name + '_' + link.target
      }
    },

    // 删除选中的节点
    async deleteSelectedNodes() {
      if (this.selectedNodes.size === 0) {
        this.$message.warning('请先选择要删除的节点')
        return
      }

      if (this.isDeleting) return

      this.isDeleting = true
      try {
        const userId = localStorage.getItem('user_id')
        const isAdmin = localStorage.getItem('userRole') === 'admin'

        if (!userId) {
          throw new Error('未获取到用户ID，请重新登录')
        }

        const response = await fetch(getApiUrl('/graph/nodes'), {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: parseInt(userId),
            is_admin: isAdmin,
            node_ids: Array.from(this.selectedNodes),
          }),
        })

        if (!response.ok) {
          throw new Error(`删除节点失败: HTTP ${response.status}`)
        }

        const result = await response.json()
        console.log('删除节点结果:', result)

        // 从本地数据中移除已删除的节点
        this.fullData.nodes = this.fullData.nodes.filter((node) => !this.selectedNodes.has(node.id))
        this.fullData.links = this.fullData.links.filter((link) => {
          const sourceId = typeof link.source === 'object' ? link.source.id : link.source
          const targetId = typeof link.target === 'object' ? link.target.id : link.target
          return !this.selectedNodes.has(sourceId) && !this.selectedNodes.has(targetId)
        })

        // 清空选中状态
        this.selectedNodes.clear()

        // 重新筛选和渲染
        this.limitInitialNodes()
        this.renderGraph(this.filteredData)

        this.$message.success(`成功删除 ${result.deleted_count} 个节点`)
      } catch (error) {
        console.error('删除节点失败:', error)
        this.$message.error(`删除节点失败: ${error.message}`)
      } finally {
        this.isDeleting = false
      }
    },

    // 清空所有选中状态
    clearSelection() {
      this.selectedNodes.clear()
      this.updateNodeSelectionStyles()
    },
  },
}
</script>

<style>
.kg-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  transition: all 0.3s ease;
}

.kg-sidebar {
  width: 320px;
  min-width: 280px;
  max-width: 400px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e2e8f0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow-y: auto;
  transition: all 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .kg-container {
    flex-direction: column;
  }

  .kg-sidebar {
    width: 100%;
    max-width: none;
    height: auto;
    max-height: 50vh;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .kg-canvas-area {
    height: calc(100vh - 50vh);
  }
}

.kg-canvas-area {
  flex: 1;
  height: 100vh;
  position: relative;
  background: #f8fafc;
}

.canvas-container {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  width: calc(100% - 32px);
  height: calc(100vh - 32px);
  position: relative;
  margin: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.node {
  stroke: #cfebfe;
  stroke-width: 1;
  cursor: pointer;
}
.node:hover {
  stroke-width: 5px;
}
.node.selected {
  stroke-width: 4px !important;
  stroke: #ff6b6b !important;
}
.node-text {
  fill: #ffffff;
  text-anchor: middle;
  font-size: 10px;
  user-select: none;
}
.link {
  stroke: #999;
  stroke-opacity: 0.6;
  stroke-width: 2.25;
}
.linksName {
  text-anchor: middle;
  fill: #4a5a6a;
  font-size: 9px;
  /* font-weight: bold; */
}
.el-icon-download {
  position: absolute;
  bottom: 20px;
  right: 20px;
  cursor: pointer;
  font: 2.5em sans-serif;
  color: #6366f1;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  transition: all 0.3s ease;
  z-index: 20;
}

.el-icon-download:hover {
  color: white;
  background: #6366f1;
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

/* 暗黑模式样式 */
.dark .kg-container {
  background: #1a1a1a;
}

.dark .kg-sidebar {
  background: #2d2d2d;
  border-right-color: #444;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
  height: 100vh;
}

.dark .kg-canvas-area {
  background: #1a1a1a;
  height: 100vh;
}

.dark .canvas-container {
  background: #2d2d2d;
  border: 1px solid #444;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark .node {
  stroke: #2c3e50;
}

.dark .node-text {
  fill: #ffffff;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.8);
}

.dark .link {
  stroke: #666;
  stroke-opacity: 0.4;
}

.dark .linksName {
  fill: #aaa;
}

.dark .el-icon-download {
  color: #8b5cf6;
  background: rgba(30, 30, 30, 0.9);
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.dark .el-icon-download:hover {
  color: white;
  background: #8b5cf6;
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.4);
}
</style>

<style scoped>
/* 原有样式保持不变 */

/* 添加加载和错误状态的样式 */
.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-text,
.error-text {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
}

.retry-button {
  padding: 8px 16px;
  background-color: #4ecdc4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-button:hover {
  background-color: #3dbbb3;
}

/* 暗黑模式下的加载和错误状态 */
.dark .loading-overlay,
.dark .error-overlay {
  background-color: rgba(26, 26, 26, 0.9);
}

.dark .loading-text,
.dark .error-text {
  color: #eee;
}

.dark .retry-button {
  background-color: #34495e;
}

.dark .retry-button:hover {
  background-color: #2c3e50;
}
</style>

<style scoped>
/* 自定义动画关键帧 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  10%,
  30%,
  50%,
  70%,
  90% {
    transform: translateX(-5px);
  }
  20%,
  40%,
  60%,
  80% {
    transform: translateX(5px);
  }
}

/* 动画类 */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}

.animate-slide-up {
  animation: slideUp 0.4s ease-out forwards;
}

.animate-shake {
  animation: shake 0.5s ease-in-out;
}
</style>
