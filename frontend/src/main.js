
import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

const app = createApp(App)

// 配置 Axios 全局默认值
axios.defaults.baseURL = 'http://127.0.0.1:8001';

app.use(ElementPlus)
app.mount('#app')