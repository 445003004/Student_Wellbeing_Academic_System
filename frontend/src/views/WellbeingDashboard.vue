<template>
  <div class="dashboard-layout">
    <header class="navbar">
      <div class="brand">
        <span class="icon">🌻</span>
        <span>Wellbeing Center</span>
      </div>
      <div class="user-menu">
        <span>Logged in as <b>Officer</b></span>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </header>

    <main class="content-container">
      <div v-if="loading" class="loading-state">Accessing confidential data...</div>

      <div v-else class="dashboard-grid">

        <div class="left-column">

          <section class="chart-card">
            <h3>📈 Weekly Trends (School-wide)</h3>
            <div class="chart-wrapper">
              <Line v-if="chartData" :data="chartData" :options="chartOptions" />
            </div>
          </section>

          <section class="lookup-card">
            <h3>🔍 Student History Lookup</h3>
            <div class="search-bar">
              <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  placeholder="Enter Student Number (e.g. u123)"
              />
              <button @click="handleSearch" class="btn-search" :disabled="searchLoading">
                {{ searchLoading ? 'Searching...' : 'Search' }}
              </button>
            </div>

            <div v-if="searchResult.length > 0" class="history-table-wrapper">
              <table class="data-table">
                <thead>
                <tr>
                  <th>Week</th>
                  <th>Stress (1-5)</th>
                  <th>Sleep (h)</th>
                  <th>Date</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="item in searchResult" :key="item.id">
                  <td>Week {{ item.week_number }}</td>
                  <td>
                      <span :class="['badge-sm', item.stress_level >= 4 ? 'bg-red' : 'bg-green']">
                        {{ item.stress_level }}
                      </span>
                  </td>
                  <td>{{ item.hours_slept }}h</td>
                  <td>{{ new Date(item.recorded_at).toLocaleDateString() }}</td>
                </tr>
                </tbody>
              </table>
            </div>
            <div v-else-if="searchPerformed" class="empty-search">
              No records found for this student.
            </div>
          </section>

        </div>

        <div class="right-column">

          <section class="risk-card">
            <div class="card-header">
              <h3>⚠️ At Risk List</h3>
              <span class="badge">{{ riskList.length }}</span>
            </div>
            <div class="risk-list-container">
              <div v-if="riskList.length === 0" class="empty-msg">No alerts active.</div>
              <div v-for="record in riskList" :key="record.id" class="student-alert-item">
                <div class="student-info">
                  <strong>{{ record.student.full_name }}</strong>
                  <small>{{ record.student.student_number }}</small>
                </div>
                <div class="alert-tags">
                  <span v-if="record.stress_level >= 4" class="tag tag-stress">High Stress</span>
                  <span v-if="record.hours_slept < 5" class="tag tag-sleep">Low Sleep</span>
                </div>
              </div>
            </div>
          </section>

          <section class="entry-card">
            <div class="tabs">
              <button
                  :class="{ active: entryMode === 'manual' }"
                  @click="entryMode = 'manual'">Manual Entry</button>
              <button
                  :class="{ active: entryMode === 'csv' }"
                  @click="entryMode = 'csv'">Batch CSV</button>
            </div>

            <form v-if="entryMode === 'manual'" @submit.prevent="submitSurvey" class="entry-form">
              <p class="helper-text">Add a single record.</p>
              <input v-model="form.student_number" placeholder="Student No. (e.g. u123)" required />
              <div class="row">
                <select v-model.number="form.week_number" required>
                  <option v-for="n in 12" :key="n" :value="n">Week {{ n }}</option>
                </select>
                <select v-model.number="form.stress_level" required>
                  <option value="" disabled>Stress</option>
                  <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
                </select>
              </div>
              <input v-model.number="form.hours_slept" type="number" placeholder="Sleep Hours" step="0.5" required />

              <button type="submit" class="btn-save">Save Record</button>
            </form>

            <div v-if="entryMode === 'csv'" class="csv-upload-box">
              <p class="helper-text">Upload CSV with columns: <code>student_number, week_number, stress_level, hours_slept</code></p>

              <input type="file" ref="fileInput" accept=".csv" @change="handleFileSelect" class="file-input" />

              <button @click="submitCsv" class="btn-upload" :disabled="!selectedFile || uploadLoading">
                {{ uploadLoading ? 'Uploading...' : 'Upload CSV' }}
              </button>

              <div v-if="uploadResult" class="upload-feedback">
                <div class="success-text">✅ Processed: {{ uploadResult.success_count }} rows</div>
                <div v-if="uploadResult.errors.length" class="error-log">
                  <strong>Errors:</strong>
                  <ul>
                    <li v-for="(err, idx) in uploadResult.errors" :key="idx">{{ err }}</li>
                  </ul>
                </div>
              </div>
            </div>

            <span v-if="msg" class="global-msg">{{ msg }}</span>
          </section>

        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getWellbeingTrends,
  getRiskAlerts,
  createSurvey,
  getStudentHistory,
  uploadCsvSurveys
} from '../api/wellbeing' // 确保这里引入了新函数
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)

const router = useRouter()
const loading = ref(true)
const msg = ref('')

// Dashboard Data
const chartData = ref(null)
const riskList = ref([])

// Entry Form Data
const entryMode = ref('manual') // 'manual' or 'csv'
const form = ref({ student_number: '', week_number: 10, stress_level: '', hours_slept: '' })

// CSV Upload Data
const selectedFile = ref(null)
const uploadLoading = ref(false)
const uploadResult = ref(null)
const fileInput = ref(null)

// Student Search Data
const searchQuery = ref('')
const searchResult = ref([])
const searchLoading = ref(false)
const searchPerformed = ref(false)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: { legend: { position: 'bottom' } }
}

onMounted(async () => {
  try {
    await loadDashboard()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
})

const loadDashboard = async () => {
  const [trendsRes, riskRes] = await Promise.all([getWellbeingTrends(), getRiskAlerts()])

  chartData.value = {
    labels: trendsRes.data.map(t => `W${t.week}`),
    datasets: [
      {
        label: 'Avg Stress',
        data: trendsRes.data.map(t => t.average_stress),
        borderColor: '#f56565',
        backgroundColor: '#f56565',
        tension: 0.3
      },
      {
        label: 'Avg Sleep (h)',
        data: trendsRes.data.map(t => t.average_sleep),
        borderColor: '#4299e1',
        backgroundColor: '#4299e1',
        tension: 0.3
      }
    ]
  }
  riskList.value = riskRes.data
}

// --- 手动录入逻辑 ---
const submitSurvey = async () => {
  try {
    await createSurvey(form.value)
    msg.value = 'Record Saved!'
    await loadDashboard()
    form.value.student_number = ''
    setTimeout(() => msg.value = '', 3000)
  } catch (e) {
    alert('Error saving data. Student ID valid?')
  }
}

// --- CSV 上传逻辑 ---
const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
  uploadResult.value = null
}

const submitCsv = async () => {
  if (!selectedFile.value) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  uploadLoading.value = true
  try {
    const res = await uploadCsvSurveys(formData)
    uploadResult.value = res.data // { success_count, errors, message }
    msg.value = 'Batch upload complete.'

    // 刷新全校数据
    await loadDashboard()

    // 清理文件输入
    if (fileInput.value) fileInput.value.value = ''
    selectedFile.value = null
  } catch (e) {
    alert('Failed to upload CSV: ' + (e.response?.data?.detail || e.message))
  } finally {
    uploadLoading.value = false
  }
}

// --- 学生查询逻辑 ---
const handleSearch = async () => {
  if (!searchQuery.value) return

  searchLoading.value = true
  searchPerformed.value = true
  searchResult.value = [] // clear previous

  try {
    const res = await getStudentHistory(searchQuery.value)
    // 按周数排序
    searchResult.value = res.data.sort((a, b) => a.week_number - b.week_number)
  } catch (e) {
    // 404 is handled by showing empty result
    console.log("Student not found or error")
  } finally {
    searchLoading.value = false
  }
}

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
/* 基础布局 */
.dashboard-layout { background-color: #f7fafc; min-height: 100vh; }
.navbar { background: #285e61; color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.brand { font-size: 1.25rem; font-weight: bold; display: flex; gap: 10px; align-items: center; }
.btn-logout { background: rgba(0,0,0,0.2); color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; transition: background 0.2s; }
.btn-logout:hover { background: rgba(0,0,0,0.3); }

.content-container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.dashboard-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 1.5rem; align-items: start; }

/* 通用卡片 */
section { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }
h3 { margin-top: 0; color: #2d3748; font-size: 1.1rem; border-bottom: 2px solid #edf2f7; padding-bottom: 10px; margin-bottom: 15px; }

/* 左侧特定样式 */
.chart-wrapper { height: 350px; }

/* 搜索区样式 */
.search-bar { display: flex; gap: 10px; margin-bottom: 1rem; }
.search-bar input { flex: 1; padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px; }
.btn-search { background: #3182ce; color: white; border: none; padding: 0 20px; border-radius: 6px; cursor: pointer; }
.btn-search:disabled { opacity: 0.7; cursor: not-allowed; }

/* 表格样式 */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th, .data-table td { text-align: left; padding: 10px; border-bottom: 1px solid #edf2f7; }
.data-table th { color: #718096; font-weight: 600; }
.badge-sm { padding: 2px 8px; border-radius: 10px; font-size: 0.8rem; font-weight: bold; color: white; }
.bg-red { background-color: #f56565; }
.bg-green { background-color: #48bb78; }

/* 右侧栏样式 */
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.badge { background: #fed7d7; color: #c53030; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 0.85rem; }
.risk-list-container { max-height: 300px; overflow-y: auto; }
.student-alert-item { background: #fff5f5; border-left: 4px solid #fc8181; padding: 10px; margin-bottom: 8px; border-radius: 0 4px 4px 0; }
.student-info { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.95rem; }
.tag { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; margin-right: 5px; text-transform: uppercase; font-weight: bold; color: white; }
.tag-stress { background: #e53e3e; }
.tag-sleep { background: #d69e2e; }

/* 录入 & CSV Tab 样式 */
.tabs { display: flex; border-bottom: 1px solid #e2e8f0; margin-bottom: 15px; }
.tabs button { flex: 1; padding: 10px; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; color: #718096; font-weight: 600; }
.tabs button.active { border-bottom-color: #2c7a7b; color: #2c7a7b; }
.tabs button:hover { background: #f7fafc; }

.entry-form, .csv-upload-box { display: flex; flex-direction: column; gap: 12px; }
.helper-text { font-size: 0.85rem; color: #718096; margin: 0; }
.helper-text code { background: #edf2f7; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
.entry-form input, .entry-form select { padding: 10px; border: 1px solid #cbd5e0; border-radius: 6px; }
.row { display: flex; gap: 10px; }
.row > * { flex: 1; }
.btn-save { background: #2c7a7b; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-upload { background: #805ad5; color: white; padding: 10px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }
.btn-upload:disabled { opacity: 0.6; }

/* CSV 反馈 */
.upload-feedback { background: #f0fff4; border: 1px solid #c6f6d5; padding: 10px; border-radius: 6px; font-size: 0.85rem; }
.success-text { color: #2f855a; font-weight: bold; }
.error-log { margin-top: 5px; color: #c53030; max-height: 100px; overflow-y: auto; }
.global-msg { text-align: center; color: #2c7a7b; font-weight: bold; margin-top: 10px; display: block; }

/* 响应式 */
@media (max-width: 768px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}
</style>
