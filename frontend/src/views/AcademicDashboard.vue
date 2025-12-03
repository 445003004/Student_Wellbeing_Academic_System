<template>
  <div class="dashboard-layout">
    <!-- 顶部导航 -->
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
      <!-- 加载中状态 -->
      <div v-if="loading" class="loading-state">Loading academic data...</div>

      <div v-else>
        <!-- 控制栏：选择课程 -->
        <div class="controls-card">
          <label>Select Module:</label>
          <select v-model="selectedCourseId" @change="fetchData" class="course-select">
            <option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.code }} - {{ course.name }}
            </option>
          </select>
        </div>

        <!-- 核心指标 KPI -->
        <div class="kpi-grid" v-if="analytics">
          <div class="kpi-card">
            <h3>Total Students</h3>
            <p class="value">{{ analytics.total_students_enrolled }}</p>
          </div>

          <div class="kpi-card" :class="getGradeStatus(analytics.average_grade)">
            <h3>Avg Grade</h3>
            <p class="value">{{ analytics.average_grade }}</p>
            <span class="status-badge">Target: >60</span>
          </div>

          <div class="kpi-card" :class="getAttendanceStatus(analytics.attendance_rate)">
            <h3>Attendance Rate</h3>
            <p class="value">{{ analytics.attendance_rate }}%</p>
            <span class="status-badge">Target: >80%</span>
          </div>
        </div>

        <!-- 图表区域 -->
        <div class="chart-section" v-if="chartData">
          <h3>Performance Analysis</h3>
          <div class="chart-wrapper">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCourses, getCourseAnalytics } from '../api/academic'
// 引入 Chart.js
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()
const loading = ref(true)
const courses = ref([])
const selectedCourseId = ref(null)
const analytics = ref(null)
const chartData = ref(null)

// 图表配置
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: { beginAtZero: true, max: 100 }
  }
}

// 初始化
onMounted(async () => {
  try {
    const res = await getCourses()
    courses.value = res.data
    if (courses.value.length > 0) {
      selectedCourseId.value = courses.value[0].id
      await fetchData()
    }
  } catch (error) {
    console.error("Failed to load courses")
  } finally {
    loading.value = false
  }
})

// 获取数据并更新图表
const fetchData = async () => {
  if (!selectedCourseId.value) return

  const res = await getCourseAnalytics(selectedCourseId.value)
  analytics.value = res.data.analytics

  // 更新图表数据
  chartData.value = {
    labels: ['Average Grade', 'Attendance Rate'],
    datasets: [{
      label: 'Performance Metrics',
      data: [analytics.value.average_grade, analytics.value.attendance_rate],
      backgroundColor: ['#4299e1', '#48bb78'],
      borderRadius: 5
    }]
  }
}

const getGradeStatus = (val) => val < 50 ? 'danger' : 'success'
const getAttendanceStatus = (val) => val < 70 ? 'danger' : 'success'

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
/* 布局样式 */
.navbar {
  background: #2d3748;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.brand { font-size: 1.2rem; font-weight: bold; display: flex; align-items: center; gap: 10px; }
.btn-logout {
  background: #e53e3e;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  margin-left: 15px;
}

.content-container { max-width: 1000px; margin: 2rem auto; padding: 0 1rem; }
.controls-card { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.course-select { padding: 0.5rem; font-size: 1rem; margin-left: 10px; border-radius: 4px; min-width: 250px; }

/* KPI 卡片 */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
.kpi-card { background: white; padding: 1.5rem; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #cbd5e0; }
.kpi-card.danger { border-top-color: #f56565; }
.kpi-card.success { border-top-color: #48bb78; }
.value { font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0; color: #2d3748; }
.status-badge { background: #edf2f7; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; color: #718096; }

/* 图表 */
.chart-section { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.chart-wrapper { height: 350px; position: relative; }
</style>
