<template>
  <div>
    <!-- 筛选区域 -->
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 max-w-6xl mx-auto">
      <div class="flex flex-col space-y-3 md:flex-row md:space-y-0 md:items-center justify-between">
        <!-- 左侧标题 -->
        <div class="text-gray-700 dark:text-gray-300 font-medium text-lg">
          <Icon icon="lucide:video" class="text-gray-500 dark:text-gray-400 w-6 h-6" />
          筛选视频
        </div>

        <!-- 中间标签组 -->
        <div class="flex-1 md:mx-4 overflow-hidden">
          <div class="flex flex-wrap gap-2">
            <!-- 岗位类型 -->
            <div
              class="flex flex-wrap gap-2 border-r-0 border-gray-200 dark:border-gray-700 px-0 md:px-3"
            >
              <button
                v-for="tag in jobTypes"
                :key="tag"
                @click="toggleTag(tag)"
                :class="[
                  'px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors tag-btn',
                  selectedTags.includes(tag)
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600',
                ]"
              >
                {{ tag }}
              </button>
            </div>

            <div
              class="hidden md:block w-full border-t-1 border-gray-200 dark:border-gray-700 my-3"
            ></div>

            <!-- 内容主题 -->
            <div
              class="flex flex-wrap gap-2 border-r-0 border-gray-200 dark:border-gray-700 px-0 md:px-3"
            >
              <button
                v-for="tag in contentTopics"
                :key="tag"
                @click="toggleTag(tag)"
                :class="[
                  'px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors tag-btn',
                  selectedTags.includes(tag)
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600',
                ]"
              >
                {{ tag }}
              </button>
            </div>

            <div
              class="hidden md:block w-full border-t-1 border-gray-200 dark:border-gray-700 my-3"
            ></div>

            <!-- 适用阶段 -->
            <div
              class="flex flex-wrap gap-2 border-r-0 border-gray-200 dark:border-gray-700 px-0 md:px-3"
            >
              <button
                v-for="tag in stages"
                :key="tag"
                @click="toggleTag(tag)"
                :class="[
                  'px-3 py-1.5 rounded-full text-sm whitespace-nowrap transition-colors tag-btn',
                  selectedTags.includes(tag)
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600',
                ]"
              >
                {{ tag }}
              </button>
            </div>
          </div>
        </div>

        <button
          @click="clearFilters"
          class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm whitespace-nowrap transition-colors mt-2 md:mt-0"
        >
          清除筛选
        </button>
      </div>
    </div>

    <!-- 视频列表区域 -->
    <div class="mt-10 max-w-6xl mx-auto">
      <div class="flex justify-between items-center mb-6">
        <h2
          class="text-xl md:text-2xl font-bold text-gray-900 dark:text-white tracking-tight leading-tight"
        >
          <i class="fas fa-star text-yellow-400 mr-2"></i>精选面试学习视频
        </h2>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          已精选 {{ filteredVideos.length }} 个高质量视频
        </span>
      </div>

      <div
        v-if="filteredVideos.length === 0"
        class="text-center py-12 bg-white dark:bg-gray-800 rounded-xl"
      >
        <i class="fas fa-video-slash text-4xl text-gray-300 dark:text-gray-600 mb-4"></i>
        <p class="text-gray-500 dark:text-gray-400">没有找到符合条件的视频，请尝试其他筛选条件</p>
        <button
          @click="clearFilters"
          class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition"
        >
          清除筛选条件
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- 单个视频卡片 -->
        <div
          v-for="video in filteredVideos"
          :key="video.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden flex flex-col"
          @click="openVideo(video.url)"
        >
          <!-- 内容区域：flex-grow 确保占据剩余空间 -->
          <div class="flex flex-col p-4 flex-grow justify-between h-[calc(320px-192px)]">
            <!-- 标题区域：固定高度，超出省略 -->
            <div class="h-12 mb-2">
              <h3 class="text-sm font-medium line-clamp-2 text-gray-900 dark:text-gray-100">
                {{ video.title }}
              </h3>
            </div>

            <!-- 标签区域：固定高度 -->
            <div class="h-8 mb-2 flex gap-2">
              <span
                v-for="(tag, index) in video.tags.slice(0, 3)"
                :key="index"
                class="px-2 py-1 text-xs rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
              >
                {{ tag }}
              </span>
            </div>

            <!-- 底部信息区域：固定在底部 -->
            <div class="flex justify-between items-center mt-auto">
              <!-- 播放量 -->
              <span class="text-xs text-gray-500 dark:text-gray-400">
                <i class="fas fa-play-circle mr-1"></i> {{ video.playCount }}
              </span>

              <!-- 平台标识 -->
              <div class="flex items-center">
                <BiliBili class="w-4 h-4 mr-1 dark:text-gray-200" />
                <span
                  class="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-500 dark:text-white"
                >
                  {{ video.platform === 'bilibili' ? 'B站' : 'YouTube' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <footer class="mt-12 text-center text-gray-500 dark:text-gray-400 text-sm">
      <p>以上视频均来源于bilibili</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import BiliBili from '@/icons/BiliBili.vue'
import { Icon } from '@iconify/vue'

export default {
  setup() {
    const darkMode = ref(false)
    const selectedTags = ref([])
    const jobTypes = ref(['技术岗', '产品岗', '运营岗', '设计岗', '市场岗', '算法岗'])

    const contentTopics = ref([
      '面试流程',
      '高频题型',
      '面试技巧',
      '岗位知识',
      '状态调整',
      '经验与案例',
      '压力面应对',
      'Offer攻略',
      '小组面试技巧',
      '避坑指南',
      '高分策略',
    ])

    const stages = ref(['实习', '零经验', '双非', '暑期', '毕业季', '转行', '校招'])
    const videos = ref([
      {
        id: 1,
        title: '狂揽Offer! 揭秘互联网大厂算法岗面试流程与技巧！',
        tags: ['算法岗', '技术岗', '面试流程', '面试技巧', 'Offer攻略'],
        url: 'https://www.bilibili.com/video/BV13C3xzuE8h',
        platform: 'bilibili',
      },
      {
        id: 2,
        title: '【面试】互联网技术岗面试经验分享',
        tags: ['技术岗', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1Xi4y1P7hZ',
        platform: 'bilibili',
      },
      {
        id: 3,
        title: '校招互联网技术岗面试技巧和学习经验（主要针对转行同学）来啦！',
        tags: ['转行', '技术岗', '校招'],
        url: 'https://www.bilibili.com/video/BV1mQ4y1h7US',
        platform: 'bilibili',
      },
      {
        id: 4,
        title: '技术面问到不会的如何临机应变？看到就是赚到',
        tags: ['面试技巧', '技术岗'],
        url: 'https://www.bilibili.com/video/BV1HZ421g7Z4',
        platform: 'bilibili',
      },
      {
        id: 5,
        title: '面试分享|23届互联网暑期实习技术岗|面试时间线+面试总结',
        tags: ['暑期', '实习', '技术岗', '面试流程'],
        url: 'https://www.bilibili.com/video/BV1Br4y1t7Js',
        platform: 'bilibili',
      },
      {
        id: 6,
        title: '【秋招】如何拿到互联网大厂技术岗 | 算法岗offer——PART3.面试必备技巧',
        tags: ['算法岗', '技术岗', '校招', 'Offer攻略'],
        url: 'https://www.bilibili.com/video/BV1he411W7cV',
        platform: 'bilibili',
      },
      {
        id: 7,
        title: '互联网技术岗求职避坑指南~大二、大三、研一、研二【欧阳同学-华为后端开发】',
        tags: ['避坑指南', '技术岗'],
        url: 'https://www.bilibili.com/video/BV1BY4y1G7Pb',
        platform: 'bilibili',
      },
      {
        id: 8,
        title: '【纯干货】产品经理面试实况录像 | 互联网大厂的应届生招聘实录',
        tags: ['产品岗'],
        url: 'https://www.bilibili.com/video/BV1pz4y167f6',
        platform: 'bilibili',
      },
      {
        id: 9,
        title: '没经验咋去面互联网产品运营？拆解面试题目、分享面试官筛人逻辑',
        tags: ['高频题型', '运营岗', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1Ky4y147wb',
        platform: 'bilibili',
      },
      {
        id: 10,
        title:
          '我是怎么拿到7家产品经理offer的？面试官最想听什么回答？ | 产品经理面试经验分享 | 面试技巧分享',
        tags: ['Offer攻略', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1Gy4y1r7jf',
        platform: 'bilibili',
      },
      {
        id: 11,
        title: '24届校招产品岗经验分享',
        tags: ['校招', '产品岗', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1tTsCesE6j',
        platform: 'bilibili',
      },
      {
        id: 12,
        title: '面试实录|互联网大厂高级产品经理专家面试',
        tags: ['产品岗', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1PBzzYZEdV',
        platform: 'bilibili',
      },
      {
        id: 13,
        title: '产品经理，面试自我介绍，可以背，但别啰嗦。',
        tags: ['面试技巧', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1JQ4y1p7hH',
        platform: 'bilibili',
      },
      {
        id: 14,
        title: '互联网产品助理岗位面试分析',
        tags: ['面试技巧', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1o3411w7fi',
        platform: 'bilibili',
      },
      {
        id: 15,
        title: '坦白局vlog｜我入职啦｜面试技巧｜互联网产品经理｜面试方法',
        tags: ['经验与案例', '面试技巧', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1Fc411R75Y',
        platform: 'bilibili',
      },
      {
        id: 16,
        title: '应届生如何进入互联网大厂做产品 | 面试经验分享',
        tags: ['经验与案例', '产品岗'],
        url: 'https://www.bilibili.com/video/BV13f4y197Fa',
        platform: 'bilibili',
      },
      {
        id: 17,
        title: '我的第一份互联网产品实习｜就算零经验，给双非文科生一个月就够了',
        tags: ['实习', '零经验', '双非', '产品岗'],
        url: 'https://www.bilibili.com/video/BV1SP4y1j7HB',
        platform: 'bilibili',
      },
      {
        id: 18,
        title: '互联网运营岗面试高频题：你为什么做运营？面试官最想听什么？面经分享',
        tags: ['高频题型', '运营岗'],
        url: 'https://www.bilibili.com/video/BV1e54y1V7ob',
        platform: 'bilibili',
      },
      {
        id: 19,
        title: '字节跳动运营岗实习生～面经干货来啦！互联网大厂offer/飞书录制',
        tags: ['实习', '运营岗'],
        url: 'https://www.bilibili.com/video/BV1C14y1W72D',
        platform: 'bilibili',
      },
      {
        id: 20,
        title: '运营岗面试被问到：如何提高转化率？',
        tags: ['运营岗', '高频题型'],
        url: 'https://www.bilibili.com/video/BV1stwreXE6C',
        platform: 'bilibili',
      },
      {
        id: 21,
        title: '【运营面试】面试如何自我介绍？',
        tags: ['高频题型', '运营岗'],
        url: 'https://www.bilibili.com/video/BV1Ja411i7Ep',
        platform: 'bilibili',
      },
      {
        id: 22,
        title: '小白版｜运营岗科普，一次性讲清各类岗位',
        tags: ['岗位知识', '运营岗'],
        url: 'https://www.bilibili.com/video/BV1p6cteVExd',
        platform: 'bilibili',
      },
      {
        id: 23,
        title: '被字节跳动录取啦~|字节跳动平面设计面试流程分享',
        tags: ['设计岗', '面试流程'],
        url: 'https://www.bilibili.com/video/BV1pT4y1L7rt',
        platform: 'bilibili',
      },
      {
        id: 24,
        title: '设计师面试，面试状态比作品集更重要！',
        tags: ['设计岗', '面试技巧'],
        url: 'https://www.bilibili.com/video/BV1hR9cYYE5s',
        platform: 'bilibili',
      },
      {
        id: 25,
        title: '秋招｜互联网大厂交互设计实习生来讲点真话🥲',
        tags: ['设计岗', '实习', '校招'],
        url: 'https://www.bilibili.com/video/BV1SC2iYGELM',
        platform: 'bilibili',
      },
      {
        id: 26,
        title: '系统设计面试6个技巧｜我面Google前的准备方法',
        tags: ['设计岗', '系统设计'],
        url: 'https://www.bilibili.com/video/BV19f4y1a7DZ',
        platform: 'bilibili',
      },
      {
        id: 27,
        title: '设计系大二成功入职腾讯的经验分享 | 渠道面试干货',
        tags: ['设计岗', '面试技巧', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1Av411h74Z',
        platform: 'bilibili',
      },
      {
        id: 28,
        title: '设计面试技巧知多少',
        tags: ['设计岗', '面试技巧'],
        url: 'https://www.bilibili.com/video/BV1qS4y1n7QT',
        platform: 'bilibili',
      },
      {
        id: 29,
        title: '市场部面试圣经！营销小白万能公式！快消互联网通吃',
        tags: ['市场岗', '高频题型'],
        url: 'https://www.bilibili.com/video/BV1W64y1i7uc',
        platform: 'bilibili',
      },
      {
        id: 30,
        title: '【市场攻略】市场部岗位面试最核心的问题怎么回答？毕业季求职攻略',
        tags: ['市场岗', '高频题型'],
        url: 'https://www.bilibili.com/video/BV1Vi4y1C7Li',
        platform: 'bilibili',
      },
      {
        id: 31,
        title: '不看后悔✅市场营销面试干货，7大必胜杀手锏，5年Marketing经验分享',
        tags: ['市场岗', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1bY411J7FE',
        platform: 'bilibili',
      },
      {
        id: 32,
        title: '市场营销岗面试：你怎么定营销策略？',
        tags: ['市场岗', '高频题型'],
        url: 'https://www.bilibili.com/video/BV1negZzrEft',
        platform: 'bilibili',
      },
      {
        id: 33,
        title:
          '分享我最常用的万能市场&零售岗专用面试分析框架｜内外企均适用，主打一个常用好用绝绝子',
        tags: ['市场岗', '高频题型'],
        url: 'https://www.bilibili.com/video/BV1Rs4y1u75T',
        platform: 'bilibili',
      },
      {
        id: 34,
        title: '【腾讯实习】【运营岗】初面面经！纯干货，已上岸',
        tags: ['运营岗'],
        url: 'https://www.bilibili.com/video/BV1aC4y1s7a9',
        platform: 'bilibili',
      },
      {
        id: 35,
        title: '秋招开启！初面面试经验大全！',
        tags: ['校招', '面试技巧'],
        url: 'https://www.bilibili.com/video/BV11UsreUE1z',
        platform: 'bilibili',
      },
      {
        id: 36,
        title: '群面不用抢角色！无领导小组面试攻略',
        tags: ['小组面试技巧'],
        url: 'https://www.bilibili.com/video/BV1MoR5YYET9',
        platform: 'bilibili',
      },
      {
        id: 37,
        title:
          '无领导小组讨论看这一篇就够了 | 答题逻辑框架 | 题型分析 | 话术模板 | 评分要素 | 角色选择 | 秋招面试干货建议收藏【北大学姐秋招面试经验分享】',
        tags: ['小组面试技巧', '高分策略', '校招'],
        url: 'https://www.bilibili.com/video/BV1kh411p7ST',
        platform: 'bilibili',
      },
      {
        id: 38,
        title:
          '无领导小组通过率100%的5个答题框架，照着思维导图拿高分！互联网&快消群面最强面试技巧！',
        tags: ['小组面试技巧', '高分策略'],
        url: 'https://www.bilibili.com/video/BV1Zf4y1g74W',
        platform: 'bilibili',
      },
      {
        id: 39,
        title: '互联网群面真题 北大学霸高分回答实录-下篇',
        tags: ['小组面试技巧'],
        url: 'https://www.bilibili.com/video/BV1YY4y137x1',
        platform: 'bilibili',
      },
      {
        id: 40,
        title: '【群面技巧】4分钟说清群面技巧丨斗鸡大会丨饥饿游戏丨苗疆养蛊',
        tags: ['面试技巧', '小组面试技巧'],
        url: 'https://www.bilibili.com/video/BV1Gu4y1U7Sb',
        platform: 'bilibili',
      },
      {
        id: 41,
        title: '【春招/暑期进】群面必过！10多场快消/互联网群面100%通过靠这个指南！',
        tags: ['校招', '暑期', '面试流程', '小组面试技巧'],
        url: 'https://www.bilibili.com/video/BV1fS421K7dG',
        platform: 'bilibili',
      },
      {
        id: 42,
        title: '【终面技巧】互联网大厂终面需要注意什么？',
        tags: ['面试技巧'],
        url: 'https://www.bilibili.com/video/BV1wY411d7GC',
        platform: 'bilibili',
      },
      {
        id: 43,
        title: '【职规日记】HR终面被刷？互联网求职HR终面你需要知道的坑！',
        tags: ['避坑指南'],
        url: 'https://www.bilibili.com/video/BV1mP4y1c78h',
        platform: 'bilibili',
      },
      {
        id: 44,
        title: '面试总是败在终面？原因都在这里',
        tags: ['状态调整', '面试技巧'],
        url: 'https://www.bilibili.com/video/BV1x64y1Y7YD',
        platform: 'bilibili',
      },
      {
        id: 45,
        title: '终面的核心策略',
        tags: ['高分策略'],
        url: 'https://www.bilibili.com/video/BV116421F7B9',
        platform: 'bilibili',
      },
      {
        id: 46,
        title: 'HR面到底会不会刷人？HR面应该怎么聊',
        tags: ['避坑指南'],
        url: 'https://www.bilibili.com/video/BV1wDdHYyEjh',
        platform: 'bilibili',
      },
      {
        id: 47,
        title: '大厂HR面都问什么？',
        tags: ['面试技巧'],
        url: 'https://www.bilibili.com/video/BV1mQ4y1r7JM',
        platform: 'bilibili',
      },
      {
        id: 48,
        title: '【互联网求职必看】大厂HR面应该注意什么？HR面有那些坑？常问哪些问',
        tags: ['避坑指南'],
        url: 'https://www.bilibili.com/video/BV1iB4y1K7hv',
        platform: 'bilibili',
      },
      {
        id: 49,
        title: '大厂面试官自我介绍示范',
        tags: ['经验与案例'],
        url: 'https://www.bilibili.com/video/BV1Vb4y187Es',
        platform: 'bilibili',
      },
      {
        id: 50,
        title: '程序员面试：如何进行自我介绍',
        tags: ['高分策略'],
        url: 'https://www.bilibili.com/video/BV1Js4y117R3',
        platform: 'bilibili',
      },
      {
        id: 51,
        title: '面试自我介绍：面试官让你自我介绍时，到底想听到什么？（含案例详解）【鹅姐|求职】',
        tags: ['高分策略', '经验与案例'],
        url: 'https://www.bilibili.com/video/BV1jy4y1j7N6',
        platform: 'bilibili',
      },
      {
        id: 52,
        title: '面试中的制胜法宝——STAR法则，手把手教你运用',
        tags: ['经验与案例'],
        url: 'https://www.bilibili.com/video/BV1hg41137kD',
        platform: 'bilibili',
      },
      {
        id: 53,
        title: '面试神技STAR法则，这样用才对！面试问:你最具成就感的事情是什么？',
        tags: ['经验与案例'],
        url: 'https://www.bilibili.com/video/BV1MS4y1Y73m',
        platform: 'bilibili',
      },
      {
        id: 54,
        title: '面试遇到“压力面”？如何反杀面试官，主动掌控面试节奏',
        tags: ['压力面应对', 'Offer攻略'],
        url: 'https://www.bilibili.com/video/BV1JL4y1H7LG',
        platform: 'bilibili',
      },
      {
        id: 55,
        title: '【23届秋招】第一次压力面，总监1v1，我竟然拿到秋招第一份offer？',
        tags: ['压力面应对', '校招', 'Offer攻略'],
        url: 'https://www.bilibili.com/video/BV1bd4y167E2',
        platform: 'bilibili',
      },
    ])
    const tagColorMap = {
      技术岗: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
      产品岗: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300',
      // 其他标签颜色映射...
    }

    const filteredVideos = computed(() => {
      if (selectedTags.value.length === 0) {
        return videos.value
      }
      return videos.value.filter((video) =>
        // 检查视频的标签是否包含用户选中的标签中的任意一个
        selectedTags.value.some((tag) => video.tags.includes(tag)),
      )
    })

    const toggleTag = (tag) => {
      if (selectedTags.value.includes(tag)) {
        selectedTags.value = selectedTags.value.filter((t) => t !== tag)
      } else {
        selectedTags.value.push(tag)
      }
    }

    const clearFilters = () => {
      selectedTags.value = []
    }

    const formatDuration = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${mins}:${secs < 10 ? '0' : ''}${secs}`
    }

    const formatPlayCount = (count) => {
      if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万次'
      }
      return count + '次'
    }

    const toggleDarkMode = () => {
      darkMode.value = !darkMode.value
      document.body.classList.toggle('dark', darkMode.value)
    }

    const openVideo = (url) => {
      window.open(url, '_blank')
    }

    onMounted(() => {
      const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)')
      darkMode.value = prefersDarkScheme.matches
      document.body.classList.toggle('dark', darkMode.value)
    })

    return {
      darkMode,
      selectedTags,
      videos,
      tagColorMap,
      filteredVideos,
      toggleTag,
      clearFilters,
      formatDuration,
      formatPlayCount,
      toggleDarkMode,
      openVideo,
      jobTypes,
      contentTopics,
      stages,
    }
  },
  components: {
    BiliBili, // 注册组件
  },
}
</script>

<style scoped>
.video-card {
  transition: all 0.3s ease;
}
.video-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.1),
    0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.thumbnail-container {
  transition: all 0.3s ease;
}
.thumbnail-container:hover {
  transform: scale(1.02);
}
.toggle-dark-btn {
  transition: all 0.3s ease;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
