import request from '../utils/request'

// 登录接口
// formData 应该包含 { username: '...', password: '...' }
// 注意：FastAPI 的 OAuth2PasswordRequestForm 需要表单数据 (Form Data)，而不是 JSON
export function login(data) {
    // 将 JSON 对象转换为 x-www-form-urlencoded 格式
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    return request({
        url: '/auth/token',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
}

// 示例：获取当前用户信息 (如果后端有这个接口)
// export function getUserInfo() {
//   return request({
//     url: '/users/me',
//     method: 'get'
//   })
// }
