<template>
  <div>
    <!-- 示例博客列表 -->
    <div class="mt-8 max-w-6xl mx-auto">
      <h2 class="text-xl font-bold text-gray-800 dark:text-gray-200 mb-4">优质技术经验博客</h2>

      <div class="space-y-4">
        <div
          v-for="blog in blogs"
          :key="blog.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-5 border border-gray-100 dark:border-gray-700 cursor-pointer hover:shadow-md transition-shadow"
          @click="openLink(blog.link)"
        >
          <h3 class="font-bold text-lg text-gray-800 dark:text-gray-100 mb-2">{{ blog.title }}</h3>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">{{ blog.description }}</p>

          <div class="flex flex-wrap justify-between items-center">
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in blog.tags"
                :key="tag"
                class="px-2 py-1 text-xs rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      selectedTags: [],
      blogs: [
        {
          id: 1,
          title: '面试市场岗位，有哪些面试官会问的问题？该如何准备？',
          tags: ['市场岗'],
          link: 'https://www.zhihu.com/question/290258004',
        },
        {
          id: 2,
          title: '4000字腾讯暑期市场营销和产品offer面经',
          tags: ['市场岗', '产品岗'],
          link: 'https://zhuanlan.zhihu.com/p/365449474',
        },
        {
          id: 3,
          title: '市场岗面试经验',
          tags: ['市场岗'],
          link: 'https://zhuanlan.zhihu.com/p/49464548',
        },
        {
          id: 4,
          title: '如何面试市场专员？面试市场专员有哪些问题？',
          tags: ['市场岗'],
          link: 'https://zhuanlan.zhihu.com/p/451420570',
        },
        {
          id: 5,
          title: '我的秋招数据分析岗面经分享（京东，美团，阿里，拼多多，vivo，滴滴）',
          tags: ['秋招', '技术岗'],
          link: 'https://blog.csdn.net/m0_59596937/article/details/136423584',
        },
        {
          id: 6,
          title: '京东前端面经（123面详细）',
          tags: ['技术岗'],
          link: 'https://blog.csdn.net/dgayuiafahf/article/details/137519017',
        },
        {
          id: 7,
          title: '计算机求职面经内容与技巧分享',
          tags: ['面经'],
          link: 'https://blog.csdn.net/weixin_62200515/article/details/147481229',
        },
        {
          id: 8,
          title: '面经|腾讯营销岗群面总结',
          tags: ['面经', '销售岗'],
          link: 'https://www.jianshu.com/p/afdd374261f9',
        },
        {
          id: 9,
          title: '我的市场职位的面试准备',
          tags: ['市场岗'],
          link: 'https://www.jianshu.com/p/e2e75da1ed99',
        },
        {
          id: 10,
          title: '我的校招面经全纪录（涉及岗位：C++后端/游戏客户端/游戏引擎/技术美术TA）',
          tags: ['校招', '面经', '技术岗'],
          link: 'https://www.jianshu.com/p/0c02c2622d1d',
        },
        {
          id: 11,
          title: '技术岗/算法岗面试如何准备？以2023秋招经历分享面试经验',
          tags: ['技术岗', '算法岗', '秋招'],
          link: 'https://zhuanlan.zhihu.com/p/644742377',
        },
        {
          id: 12,
          title: '致程序员：过了一面二面，千万别栽在HR面——70道HR面试题分享',
          tags: ['面经', 'HR面'],
          link: 'https://zhuanlan.zhihu.com/p/87908851',
        },
        {
          id: 13,
          title: '从面试官视角，谈技术岗面试方法论',
          tags: ['技术岗', '面经'],
          link: 'https://zhuanlan.zhihu.com/p/404796313',
        },
        {
          id: 14,
          title: 'IT技术岗面试技巧？',
          tags: ['技术岗', '面经'],
          link: 'https://www.zhihu.com/question/23813698',
        },
        {
          id: 15,
          title: '【面试千问】技术岗面试的细节问题',
          tags: ['技术岗', '面经'],
          link: 'https://zhuanlan.zhihu.com/p/649162599',
        },
        {
          id: 16,
          title: '面试经验 | AI 算法工程师（面试官角度）',
          tags: ['算法岗', '面经'],
          link: 'https://zhuanlan.zhihu.com/p/483295856',
        },
        {
          id: 17,
          title: '计算机专业如何准备国企的面试和笔试？',
          tags: ['国企', '面经'],
          link: 'https://www.zhihu.com/question/529128853',
        },
        {
          id: 18,
          title:
            '保姆级面经｜我是如何拿到互联网大厂“网易”&知识巨擎“得到”的双offer【面试问题全公开】',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/385863700',
        },
        {
          id: 19,
          title:
            '【面经系列】万字面试分享贴！从十二个角度解析面试全流程！附互联网公司Offer难度系数分析',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/597899784',
        },
        {
          id: 20,
          title: '面经分享！一线互联网公司面试及求职建议',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/104861607',
        },
        {
          id: 21,
          title: '最新精心整理的互联网大厂笔面试真题',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/32290464954',
        },
        {
          id: 22,
          title: '互联网大厂日常实习生面经(滴滴，京东，字节跳动，快手)',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/338324103',
        },
        {
          id: 23,
          title: '春招互联网面经经验分享',
          tags: ['春招', '面经'],
          link: 'https://zhuanlan.zhihu.com/p/360458619',
        },
        {
          id: 24,
          title: '把大厂都面试一遍后，我总结了14条面试经验',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/160842088',
        },
        {
          id: 25,
          title: '社招面经｜一年工作经验跳槽字节跳动社招经历分享',
          tags: ['面经'],
          link: 'https://zhuanlan.zhihu.com/p/92368343',
        },
      ],
    }
  },
  methods: {
    toggleTag(tag) {
      if (this.selectedTags.includes(tag)) {
        this.selectedTags = this.selectedTags.filter((t) => t !== tag)
      } else {
        this.selectedTags.push(tag)
      }
    },
    clearFilters() {
      this.selectedTags = []
    },
    openLink(url) {
      window.open(url, '_blank')
    },
  },
}
</script>

<style>
/* 确保不会出现水平滚动条 */
html,
body {
  overflow-x: hidden;
}

/* 平滑的暗黑模式切换 */
body {
  transition:
    background-color 0.3s,
    color 0.3s;
}
</style>
