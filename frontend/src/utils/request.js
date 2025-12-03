import axios from 'axios'

// 1. 创建 Axios 实例
const service = axios.create({
    baseURL: 'http://127.0.0.1:8080',
    timeout: 5000, // 请求超时时间 (5秒)
    headers: { 'Content-Type': 'application/json' }
})

// 2. 请求拦截器 (Request Interceptor)
// 在请求发送出去之前执行：自动把 Token 加到 Header 里
service.interceptors.request.use(
    (config) => {
        // 假设登录时我们将 Token 存到了 localStorage 的 'token' 字段中
        const token = localStorage.getItem('token')

        if (token) {
            // 这里的格式必须是 "Bearer <token>"，注意 Bearer 后面的空格
            config.headers['Authorization'] = `Bearer ${token}`
        }

        return config
    },
    (error) => {
        console.error('Request Error:', error)
        return Promise.reject(error)
    }
)

// 3. 响应拦截器 (Response Interceptor)
// 在收到后端响应后执行：统一处理错误 (如 401 未授权)
service.interceptors.response.use(
    (response) => {
        // 2xx 范围内的状态码都会触发该函数
        // 也可以在这里直接返回 response.data，这样组件里就不用写 .data 了
        return response
    },
    (error) => {
        // 超出 2xx 范围的状态码都会触发该函数
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 401 Unauthorized: Token 过期或无效
                    console.warn('Token expired or invalid. Redirecting to login...')

                    // 清除本地存储的过期 Token
                    localStorage.removeItem('token')
                    localStorage.removeItem('role')
                    localStorage.removeItem('username')

                    // 强制跳转回登录页 (简单粗暴但有效)
                    window.location.href = '/login'
                    break

                case 403:
                    // 403 Forbidden: 权限不足 (如 Course Director 试图访问 Wellbeing 数据)
                    console.error('Access Forbidden: You do not have permission.')
                    alert('Access Denied: You do not have permission to view this resource.')
                    break

                case 404:
                    console.error('Resource not found')
                    break

                case 500:
                    console.error('Server Error')
                    break

                default:
                    console.error('An error occurred:', error.message)
            }
        } else {
            // 网络错误 (Server down)
            console.error('Network Error / Server Down')
            alert('Network Error: Please check if the backend server is running.')
        }

        return Promise.reject(error)
    }
)

export default service
