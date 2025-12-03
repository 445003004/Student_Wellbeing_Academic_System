<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo-icon">🎓</div>
        <h1>Student Wellbeing System</h1>
        <p class="subtitle">Secure Data Management Portal</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label>Username</label>
          <input
              v-model="form.username"
              type="text"
              placeholder="Enter username"
              required
              :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input
              v-model="form.password"
              type="password"
              placeholder="Enter password"
              required
              :disabled="loading"
          />
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? 'Authenticating...' : 'Login' }}
        </button>

        <!-- 错误提示 Banner -->
        <div v-if="errorMessage" class="error-banner">
          {{ errorMessage }}
        </div>
      </form>

      <!-- 演示专用提示 (Presentation Helper) -->
<!--      <div class="demo-help">-->
<!--        <p>Demo Credentials:</p>-->
<!--        <div class="credential-row">-->
<!--          <span class="role">Course Director:</span>-->
<!--          <code>director</code> / <code>director123</code>-->
<!--        </div>-->
<!--        <div class="credential-row">-->
<!--          <span class="role">Wellbeing Officer:</span>-->
<!--          <code>officer</code> / <code>officer123</code>-->
<!--        </div>-->
<!--      </div>-->
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await login(form.value)
    // 解构后端返回的数据
    const { access_token, role, username } = response.data

    // 存入 LocalStorage
    localStorage.setItem('token', access_token)
    localStorage.setItem('role', role)
    localStorage.setItem('username', username)

    // 路由跳转逻辑
    if (role === 'course_director') {
      router.push('/academic/dashboard')
    } else if (role === 'wellbeing_officer') {
      router.push('/wellbeing/dashboard')
    } else {
      errorMessage.value = 'Unknown Role'
    }
  } catch (error) {
    if (error.response && error.response.status === 401) {
      errorMessage.value = '❌ Invalid username or password'
    } else {
      errorMessage.value = '⚠️ System Error: Backend not reachable'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* 紫色渐变背景 */
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 15px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 420px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-icon { font-size: 3rem; margin-bottom: 10px; }
h1 { font-size: 1.5rem; color: #2d3748; margin: 0; }
.subtitle { color: #718096; font-size: 0.9rem; margin-top: 5px; }

.form-group { margin-bottom: 1.5rem; }
label { display: block; margin-bottom: 0.5rem; color: #4a5568; font-weight: 600; font-size: 0.9rem; }
input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  transition: border-color 0.2s;
}
input:focus { border-color: #667eea; outline: none; }

.login-btn {
  width: 100%;
  padding: 0.8rem;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.login-btn:hover:not(:disabled) { background-color: #5a67d8; }
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; }

.error-banner {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fff5f5;
  color: #c53030;
  border-radius: 6px;
  text-align: center;
  font-size: 0.9rem;
  border: 1px solid #feb2b2;
}

.demo-help {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
  font-size: 0.85rem;
  color: #718096;
}
.credential-row {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
}
code {
  background: #edf2f7;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: #2d3748;
}
</style>
<!--<template>-->
<!--  <div class="login-container">-->
<!--    <h2>System Login</h2>-->
<!--    <form @submit.prevent="handleLogin">-->
<!--      <div>-->
<!--        <label>Username:</label>-->
<!--        <input v-model="form.username" type="text" placeholder="director or officer" required />-->
<!--      </div>-->
<!--      <div>-->
<!--        <label>Password:</label>-->
<!--        <input v-model="form.password" type="password" placeholder="password" required />-->
<!--      </div>-->
<!--      <button type="submit" :disabled="loading">-->
<!--        {{ loading ? 'Logging in...' : 'Login' }}-->
<!--      </button>-->
<!--      <p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>-->
<!--    </form>-->
<!--  </div>-->
<!--</template>-->

<!--<script setup>-->
<!--import { ref } from 'vue'-->
<!--import { useRouter } from 'vue-router'-->
<!--import { login } from '@/api/auth' // 导入我们刚才定义的 API-->

<!--const router = useRouter()-->
<!--const form = ref({-->
<!--  username: '',-->
<!--  password: ''-->
<!--})-->
<!--const loading = ref(false)-->
<!--const errorMessage = ref('')-->

<!--const handleLogin = async () => {-->
<!--  loading.value = true-->
<!--  errorMessage.value = ''-->

<!--  try {-->
<!--    // 1. 调用登录接口-->
<!--    const response = await login(form.value)-->

<!--    // 2. 提取数据 (后端返回: { access_token, role, ... })-->
<!--    const { access_token, role, username } = response.data-->

<!--    // 3. 存入 localStorage-->
<!--    localStorage.setItem('token', access_token)-->
<!--    localStorage.setItem('role', role)-->
<!--    localStorage.setItem('username', username)-->

<!--    // 4. 根据角色跳转到不同的 Dashboard-->
<!--    if (role === 'course_director') {-->
<!--      await router.push('/academic/dashboard')-->
<!--    } else if (role === 'wellbeing_officer') {-->
<!--      await router.push('/wellbeing/dashboard')-->
<!--    } else {-->
<!--      await router.push('/') // 默认页-->
<!--    }-->

<!--  } catch (error) {-->
<!--    console.error(error)-->
<!--    errorMessage.value = 'Login failed: Invalid username or password.'-->
<!--  } finally {-->
<!--    loading.value = false-->
<!--  }-->
<!--}-->
<!--</script>-->
