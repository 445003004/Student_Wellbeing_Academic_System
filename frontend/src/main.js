//import './plugins/axios'
// import { createApp } from 'vue'
// import App from './App.vue'
//
// createApp(App).mount('#app')

import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // 引入我们配置好的路由规则

// 1. 创建 Vue 应用实例
const app = createApp(App).use(router)

// 2. 挂载路由插件
// 这让我们可以使用 <router-view> 和 this.$router / useRouter()
app.use(router)

// 3. 挂载到 index.html 中的 <div id="app"></div>
app.mount('#app')
