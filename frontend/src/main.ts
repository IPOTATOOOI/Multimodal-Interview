import './assets/main.css'
import 'remixicon/fonts/remixicon.css'
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'
import 'jsvectormap/dist/jsvectormap.css'
import 'flatpickr/dist/flatpickr.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { createPinia } from 'pinia'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.ts'
const pinia = createPinia()

const app = createApp(App)

app.use(router)
app.use(ElementPlus)
app.use(pinia)

app.mount('#app')

// 全局设置：根据需要设置isFullName的值
// 这里设置为false，使用简短名称"面工坊"
// 如果需要使用完整名称"职面工坊"，将值改为true
import { useAppStore } from './store/app'
const appStore = useAppStore()
appStore.setFullName(true)
