import { defineStore } from 'pinia'

import useDocumentStore from './documentStore'
import { useDocumentListStore } from './documentListStore'

export { useDocumentStore, useDocumentListStore }
interface MenuInfoInterface {
  type: string
  display: string
  x: string
  y: string
}
export const useGlobalStore = defineStore('globalStore', {
  state: () => {
    return {
      menuInfo: {
        //右键菜单的信息
        type: 'common', //菜单类型
        display: 'none',
        x: '0px',
        y: '0px',
      },
    }
  },

  actions: {
    setMenuInfo(value: MenuInfoInterface) {
      this.menuInfo = value
    },

    setMenuInfoColumn(key: 'display' | 'x' | 'y' | 'type', value: string) {
      this.menuInfo[key] = value
    },
  },
})
