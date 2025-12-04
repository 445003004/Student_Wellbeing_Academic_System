<template>
  <div class="dashboard-layout">
    <header class="navbar">
      <div class="brand">
        <span class="icon">📊</span>
        <span>Academic Dashboard</span>
      </div>
      <div class="user-menu">
        <span>Logged in as <b>Director</b></span>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </header>

    <main class="content-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div> Loading academic data...
      </div>

      <div v-else class="dashboard-content">
        
        <section class="overview-section">
          <div class="card control-panel">
            <div class="panel-header">
              <h3>📚 Course Overview</h3>
              <select v-model="selectedCourseId" @change="fetchData" class="course-select">
                <option v-for="course in courses" :key="course.id" :value="course.id">
                  {{ course.code }} - {{ course.name }}
                </option>
              </select>
            </div>
            
            <div class="kpi-row" v-if="analytics">
              <div class="kpi-item">
                <span class="label">Enrolled</span>
                <span class="value">{{ analytics.total_students_enrolled }}</span>
              </div>
              <div class="kpi-item" :class="getGradeStatus(analytics.average_grade)">
                <span class="label">Avg Grade</span>
                <span class="value">{{ analytics.average_grade }}</span>
              </div>
              <div class="kpi-item" :class="getAttendanceStatus(analytics.attendance_rate)">
                <span class="label">Attendance</span>
                <span class="value">{{ analytics.attendance_rate }}%</span>
              </div>
            </div>

            <div class="chart-wrapper" v-if="chartData">
              <Bar :data="chartData" :options="chartOptions" />
            </div>
          </div>
        </section>

        <div class="columns-grid">
          
          <div class="column">
            <div class="card lookup-card">
              <h3>🔍 Student Lookup</h3>
              <div class="search-box">
                <input 
                  v-model="searchQuery" 
                  @keyup.enter="handleSearch"
                  placeholder="Enter Student No. (e.g. u123)" 
                />
                <button @click="handleSearch" :disabled="searchLoading">
                  {{ searchLoading ? 'Searching...' : 'Search' }}
                </button>
              </div>

              <div v-if="studentReport" class="student-report">
                <div class="student-header">
                  <div>
                    <h4>{{ studentReport.student.full_name }}</h4>
                    <span class="email-text">{{ studentReport.student.email }}</span>
                  </div>
                  <span class="id-badge">{{ studentReport.student.student_number }}</span>
                </div>
                
                <div class="tabs">
                  <button 
                    :class="{active: tab==='grades'}" 
                    @click="tab='grades'">Grades</button>
                  <button 
                    :class="{active: tab==='attendance'}" 
                    @click="tab='attendance'">Attendance</button>
                </div>

                <div v-if="tab==='grades'" class="scroll-list">
                  <table class="data-table">
                    <thead><tr><th>Module</th><th>Task</th><th>Score</th></tr></thead>
                    <tbody>
                      <tr v-for="g in studentReport.grades" :key="g.id">
                        <td><span class="code-tag">{{ g.course_code }}</span></td>
                        <td>{{ g.assignment_title }}</td>
                        <td>
                          <span :class="['score-badge', g.score < 50 ? 'fail' : 'pass']">
                            {{ g.score }}
                          </span>
                        </td>
                      </tr>
                      <tr v-if="studentReport.grades.length === 0">
                        <td colspan="3" class="text-center">No grades recorded.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div v-if="tab==='attendance'" class="scroll-list">
                  <table class="data-table">
                    <thead><tr><th>Date</th><th>Module</th><th>Status</th></tr></thead>
                    <tbody>
                      <tr v-for="a in studentReport.attendances" :key="a.id">
                        <td>{{ new Date(a.date).toLocaleDateString() }}</td>
                        <td><span class="code-tag">{{ a.course_code }}</span></td>
                        <td>
                          <span :class="['status-dot', a.status]"></span> 
                          {{ capitalize(a.status) }}
                        </td>
                      </tr>
                      <tr v-if="studentReport.attendances.length === 0">
                        <td colspan="3" class="text-center">No attendance records.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div v-else-if="searchPerformed" class="no-result">
                <p>No student found with that number.</p>
              </div>
            </div>
          </div>

          <div class="column">
            <div class="card alert-card">
              <div class="card-header">
                <h3>⚠️ Academic Alerts</h3>
                <span class="badge-count" v-if="alertList.length > 0">{{ alertList.length }}</span>
              </div>
              <p class="subtitle">Students with Failed Modules (Score &lt; 50)</p>
              
              <div class="alert-list-container">
                <div v-if="alertList.length === 0" class="empty-state">
                  <span>✅</span> All students are passing.
                </div>
                
                <div v-else v-for="item in alertList" :key="item.student.student_number" class="alert-item">
                  <div class="alert-info">
                    <strong>{{ item.student.full_name }}</strong>
                    <small>{{ item.student.student_number }}</small>
                  </div>
                  <div class="alert-metrics">
                    <div class="metric">
                      <span class="label">Avg Score</span>
                      <span :class="{'text-danger': item.average_score < 40}">{{ item.average_score }}</span>
                    </div>
                    <div class="metric warning">
                      <span class="label">Fails</span>
                      <strong>{{ item.failed_courses_count }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// 引入所有需要的 API 函数
import { getCourses, getCourseAnalytics, getAcademicAlerts, getStudentDetails } from '../api/academic'
// 引入 Chart.js 组件
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

// 注册 Chart.js 组件
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()
const loading = ref(true)

// --- 数据状态 ---
const courses = ref([])
const selectedCourseId = ref(null)
const analytics = ref(null)
const chartData = ref(null)

const alertList = ref([])
const searchQuery = ref('')
const searchLoading = ref(false)
const searchPerformed = ref(false)
const studentReport = ref(null)
const tab = ref('grades') // 当前选中的 Tab: 'grades' 或 'attendance'

// --- 图表配置 ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' }
  },
  scales: {
    y: { beginAtZero: true, max: 100 }
  }
}

// --- 初始化 ---
onMounted(async () => {
  try {
    // 1. 获取课程列表
    const coursesRes = await getCourses()
    courses.value = coursesRes.data

    // 2. 获取预警名单
    const alertsRes = await getAcademicAlerts()
    alertList.value = alertsRes.data

    // 3. 默认选中第一门课并加载数据
    if (courses.value.length > 0) {
      selectedCourseId.value = courses.value[0].id
      await fetchData()
    }
  } catch (error) {
    console.error("Failed to load dashboard data:", error)
  } finally {
    loading.value = false
  }
})

// --- 获取课程分析数据 ---
const fetchData = async () => {
  if (!selectedCourseId.value) return

  try {
    const res = await getCourseAnalytics(selectedCourseId.value)
    analytics.value = res.data.analytics

    // 更新图表
    chartData.value = {
      labels: ['Average Grade', 'Attendance Rate (%)'],
      datasets: [{
        label: res.data.course_code, // 使用课程代码作为标签
        data: [analytics.value.average_grade, analytics.value.attendance_rate],
        backgroundColor: ['#4299e1', '#48bb78'],
        borderRadius: 6,
        barThickness: 50
      }]
    }
  } catch (e) {
    console.error("Error fetching course analytics", e)
  }
}

// --- 学生查询逻辑 ---
const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  searchLoading.value = true
  searchPerformed.value = true
  studentReport.value = null
  
  try {
    const res = await getStudentDetails(searchQuery.value)
    studentReport.value = res.data
  } catch (e) {
    // 404 会在这里被捕获
    console.log("Student not found")
  } finally {
    searchLoading.value = false
  }
}

// --- 辅助函数 ---
const getGradeStatus = (val) => val < 50 ? 'danger' : 'success'
const getAttendanceStatus = (val) => val < 70 ? 'danger' : 'success'
const capitalize = (s) => s.charAt(0).toUpperCase() + s.slice(1)

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
/* 基础布局 */
.dashboard-layout { background-color: #f7fafc; min-height: 100vh; font-family: 'Segoe UI', sans-serif; }
.navbar { background: #2d3748; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.brand { font-size: 1.25rem; font-weight: bold; display: flex; align-items: center; gap: 10px; }
.btn-logout { background: #e53e3e; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-weight: 500; transition: background 0.2s; }
.btn-logout:hover { background: #c53030; }

.content-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.loading-state { text-align: center; color: #718096; margin-top: 50px; font-size: 1.1rem; }

/* 通用卡片 */
.card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; height: 100%; display: flex; flex-direction: column; }
h3 { margin: 0 0 1rem 0; color: #2d3748; font-size: 1.1rem; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; }

/* 第一部分：课程概览 */
.overview-section { margin-bottom: 1.5rem; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.course-select { padding: 8px; border: 1px solid #cbd5e0; border-radius: 6px; font-size: 1rem; min-width: 250px; }

.kpi-row { display: flex; gap: 2rem; margin-bottom: 1.5rem; }
.kpi-item { background: #f7fafc; padding: 10px 20px; border-radius: 8px; flex: 1; text-align: center; border: 1px solid #edf2f7; }
.kpi-item .label { display: block; font-size: 0.85rem; color: #718096; margin-bottom: 5px; }
.kpi-item .value { font-size: 1.5rem; font-weight: bold; color: #2d3748; }
.kpi-item.danger .value { color: #e53e3e; }
.kpi-item.success .value { color: #38a169; }

.chart-wrapper { height: 300px; position: relative; }

/* 第二部分：分栏布局 */
.columns-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 1.5rem; align-items: start; }
@media (max-width: 768px) { .columns-grid { grid-template-columns: 1fr; } }

/* 左栏：搜索 */
.search-box { display: flex; gap: 10px; margin-bottom: 1rem; }
.search-box input { flex: 1; padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; }
.search-box button { background: #3182ce; color: white; border: none; padding: 0 20px; border-radius: 6px; cursor: pointer; transition: background 0.2s; }
.search-box button:hover { background: #2b6cb0; }
.search-box button:disabled { background: #bee3f8; cursor: not-allowed; }

.student-report { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.student-header { display: flex; justify-content: space-between; align-items: flex-start; background: #ebf8ff; padding: 12px; border-radius: 6px; margin-bottom: 10px; }
.email-text { font-size: 0.85rem; color: #718096; display: block; margin-top: 2px; }
.id-badge { background: #2b6cb0; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-family: monospace; }

.tabs { display: flex; gap: 10px; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
.tabs button { background: none; border: none; padding: 8px 12px; cursor: pointer; color: #718096; font-weight: 600; border-bottom: 2px solid transparent; }
.tabs button.active { color: #3182ce; border-bottom-color: #3182ce; }

.scroll-list { max-height: 350px; overflow-y: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th { text-align: left; color: #718096; font-weight: 600; padding: 8px; border-bottom: 1px solid #edf2f7; position: sticky; top: 0; background: white; }
.data-table td { padding: 8px; border-bottom: 1px solid #f7fafc; }
.code-tag { background: #edf2f7; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; }
.score-badge { padding: 2px 8px; border-radius: 10px; font-size: 0.85rem; font-weight: bold; }
.score-badge.pass { background: #c6f6d5; color: #22543d; }
.score-badge.fail { background: #fed7d7; color: #822727; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.present { background: #48bb78; }
.status-dot.absent { background: #f56565; }
.status-dot.late { background: #ecc94b; }
.no-result { text-align: center; color: #a0aec0; padding: 2rem; font-style: italic; }

/* 右栏：预警 */
.alert-card .card-header { display: flex; justify-content: space-between; align-items: center; }
.badge-count { background: #e53e3e; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
.subtitle { font-size: 0.85rem; color: #718096; margin-top: -10px; margin-bottom: 15px; }
.alert-list-container { max-height: 500px; overflow-y: auto; flex: 1; }
.empty-state { text-align: center; padding: 2rem; color: #718096; background: #f0fff4; border-radius: 6px; }
.alert-item { background: #fff5f5; border: 1px solid #fed7d7; border-left: 4px solid #f56565; padding: 12px; border-radius: 4px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
.alert-info strong { display: block; color: #2d3748; }
.alert-info small { color: #718096; }
.alert-metrics { display: flex; gap: 15px; }
.metric { display: flex; flex-direction: column; align-items: center; }
.metric .label { font-size: 0.65rem; text-transform: uppercase; color: #718096; }
.metric strong { font-size: 1.1rem; color: #c53030; }
.text-danger { color: #c53030; font-weight: bold; }
</style>