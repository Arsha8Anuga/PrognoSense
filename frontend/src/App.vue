<script setup>
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const API_URL = ''   // lewat nginx (/api, /health); dev: proxy Vite

const backendOnline = ref(false)
const apiStatusText = ref('Memeriksa server...')
const selectedFile = ref(null)
const isProcessing = ref(false)
const result = ref(null)
const errorMessage = ref('')
const copySuccess = ref(false)

// Tanggal Saat Ini
const currentDate = new Intl.DateTimeFormat('id-ID', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric'
}).format(new Date())

// 1. Memeriksa Status Backend FastAPI
const checkBackend = async () => {
  try {
    const res = await fetch(`${API_URL}/health`)
    if (!res.ok) throw new Error()
    const data = await res.json()
    backendOnline.value = true
    apiStatusText.value = `Backend: ${String(data.status || 'Online').toUpperCase()}`
  } catch {
    backendOnline.value = false
    apiStatusText.value = 'Backend Offline'
  }
}

// 2. Event Handler File Upload
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const extension = file.name.split('.').pop().toLowerCase()
  if (!['csv', 'txt'].includes(extension)) {
    alert('Format file tidak didukung. Gunakan file CSV atau TXT.')
    return
  }

  selectedFile.value = file
  result.value = null
  errorMessage.value = ''
}

const removeFile = () => {
  selectedFile.value = null
  result.value = null
  errorMessage.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 3. Menjalankan Prediksi ke Backend
const runPrediction = async () => {
  if (!selectedFile.value) return

  isProcessing.value = true
  errorMessage.value = ''
  result.value = null

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    const res = await fetch(`${API_URL}/api/prediksi`, {
      method: 'POST',
      body: formData
    })

    const rawText = await res.text()
    let parsedData

    try {
      parsedData = JSON.parse(rawText)
    } catch {
      parsedData = { response: rawText }
    }

    if (!res.ok) {
      const detail = parsedData.detail || parsedData.message || rawText || 'Terjadi kesalahan saat memproses data.'
      throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    }

    result.value = parsedData
  } catch (err) {
    errorMessage.value = err.message || 'Gagal menghubungi server prediksi. Pastikan backend aktif.'
  } finally {
    isProcessing.value = false
  }
}

// 4. Salin Output JSON
const copyOutput = async () => {
  if (!result.value) return
  try {
    await navigator.clipboard.writeText(JSON.stringify(result.value, null, 2))
    copySuccess.value = true
    setTimeout(() => {
      copySuccess.value = false
    }, 1500)
  } catch {
    alert('Tidak dapat menyalin hasil secara otomatis.')
  }
}

onMounted(checkBackend)
</script>

<template>
  <div class="flex min-h-screen bg-slate-50 font-sans text-slate-900">
    <!-- SIDEBAR -->
    <aside class="w-64 bg-slate-900 text-white p-6 flex flex-col shrink-0 hidden md:flex">
      <div class="flex items-center gap-3 mb-10">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center text-xl font-extrabold text-white">
          P
        </div>
        <div>
          <h2 class="font-bold text-base tracking-tight">PrognoSense</h2>
          <span class="text-[10px] text-slate-400 tracking-wider block">INTELLIGENT INDUSTRY</span>
        </div>
      </div>

      <div class="text-[10px] font-bold text-slate-400 tracking-widest mb-3 px-2">MENU UTAMA</div>

      <nav class="space-y-1">
        <a href="#dashboard" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium bg-slate-800 text-white shadow-inner">
          <span class="text-base">▦</span> Dashboard
        </a>
        <a href="#upload" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
          <span class="text-base">⇧</span> Analisis Data
        </a>
        <a href="#results" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
          <span class="text-base">▤</span> Hasil Prediksi
        </a>
      </nav>

      <div class="mt-auto p-4 border border-slate-800 rounded-xl bg-slate-950/50">
        <p class="text-xs font-semibold mb-1 text-slate-200">◈ Predictive Maintenance</p>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          Sistem analisis berbasis AI untuk memprediksi Remaining Useful Life (RUL) mesin industri.
        </p>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-1 min-w-0">
      <!-- TOPBAR -->
      <header class="bg-white border-b border-slate-200 px-8 py-5 flex items-center justify-between gap-4">
        <div>
          <div class="text-xs text-slate-500 mb-1">Workspace / <span class="text-cyan-600 font-semibold">Dashboard</span></div>
          <h1 class="text-xl font-bold tracking-tight">Machine Health Monitoring</h1>
        </div>

        <Badge :variant="backendOnline ? 'default' : 'destructive'" class="px-3 py-1.5 flex items-center gap-2 text-xs">
          <span class="w-2 h-2 rounded-full" :class="backendOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'"></span>
          {{ apiStatusText }}
        </Badge>
      </header>

      <div class="max-w-7xl mx-auto p-8 space-y-6">
        <!-- WELCOME SECTION -->
        <div class="flex flex-col md:flex-row justify-between items-start gap-4">
          <div>
            <h2 class="text-2xl font-bold tracking-tight mb-1">Selamat Datang di PrognoSense 👋</h2>
            <p class="text-sm text-slate-500 max-w-2xl leading-relaxed">
              Pantau kesehatan mesin dan lakukan analisis estimasi sisa umur operasional mesin (RUL) menggunakan data sensor secara real-time.
            </p>
          </div>
          <div class="bg-white border border-slate-200 px-4 py-2 rounded-lg text-xs text-slate-600 font-medium whitespace-nowrap shadow-sm">
            {{ currentDate }}
          </div>
        </div>

        <!-- STATS CARDS -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
          <Card>
            <CardHeader class="flex flex-row items-center justify-between pb-2">
              <CardDescription class="text-xs font-medium">Status Backend</CardDescription>
              <div class="w-8 h-8 rounded-lg bg-cyan-50 text-cyan-600 flex items-center justify-center font-bold">⌁</div>
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-extrabold">{{ backendOnline ? 'ONLINE' : 'OFFLINE' }}</div>
              <p class="text-[11px] text-slate-500 mt-1">Koneksi ke FastAPI server</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between pb-2">
              <CardDescription class="text-xs font-medium">File Dataset</CardDescription>
              <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">▤</div>
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-extrabold">{{ selectedFile ? '1' : '0' }}</div>
              <p class="text-[11px] text-slate-500 mt-1">File terpilih untuk dianalisis</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader class="flex flex-row items-center justify-between pb-2">
              <CardDescription class="text-xs font-medium">Status Analisis</CardDescription>
              <div class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center font-bold">◷</div>
            </CardHeader>
            <CardContent>
              <div class="text-2xl font-extrabold">
                <template v-if="isProcessing">Memproses...</template>
                <template v-else-if="result">Selesai</template>
                <template v-else-if="errorMessage">Gagal</template>
                <template v-else>Belum ada</template>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">Status eksekusi prediksi</p>
            </CardContent>
          </Card>
        </div>

        <!-- UPLOAD PANEL -->
        <Card id="upload">
          <CardHeader class="flex flex-row items-start justify-between">
            <div>
              <CardTitle class="text-base">Unggah Dataset Mesin</CardTitle>
              <CardDescription class="text-xs mt-1">Masukkan data sensor (.csv atau .txt) untuk memulai estimasi RUL</CardDescription>
            </div>
            <Badge variant="outline" class="text-cyan-700 bg-cyan-50 border-cyan-200">LANGKAH 01</Badge>
          </CardHeader>
          <CardContent class="space-y-4">
            <div class="border-2 border-dashed border-slate-200 bg-slate-50/50 hover:bg-cyan-50/30 hover:border-cyan-400 rounded-xl p-8 text-center transition-all">
              <input
                type="file"
                id="csvFile"
                accept=".csv,.txt"
                @change="handleFileUpload"
                class="hidden"
              />
              <label for="csvFile" class="cursor-pointer flex flex-col items-center">
                <div class="w-12 h-12 rounded-xl bg-cyan-100 text-cyan-700 flex items-center justify-center text-xl font-bold mb-3">
                  ⇧
                </div>
                <h4 class="text-sm font-semibold text-slate-800 mb-1">Unggah dataset untuk dianalisis</h4>
                <p class="text-xs text-slate-500">Klik di sini untuk memilih file <span class="text-cyan-600 font-semibold">.csv</span> atau <span class="text-cyan-600 font-semibold">.txt</span> dari komputer Anda</p>
              </label>
            </div>

            <!-- FILE INFO BADGE -->
            <div v-if="selectedFile" class="flex items-center justify-between p-3.5 bg-white border border-slate-200 rounded-lg shadow-sm">
              <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center text-xs font-bold">
                  FILE
                </div>
                <div>
                  <div class="text-xs font-semibold text-slate-800">{{ selectedFile.name }}</div>
                  <div class="text-[11px] text-slate-500">{{ formatFileSize(selectedFile.size) }}</div>
                </div>
              </div>
              <Button variant="ghost" size="sm" class="text-red-500 hover:text-red-700 hover:bg-red-50" @click="removeFile">
                ✕ Hapus
              </Button>
            </div>

            <div class="flex items-center justify-between pt-2">
              <span class="text-[11px] text-slate-500">Pastikan dataset memiliki kolom kriteria sensor yang sesuai.</span>
              <Button :disabled="!selectedFile || isProcessing" @click="runPrediction" class="bg-cyan-600 hover:bg-cyan-700 text-white">
                {{ isProcessing ? 'Memproses Data...' : 'Jalankan Prediksi →' }}
              </Button>
            </div>
          </CardContent>
        </Card>

        <!-- RESULT PANEL -->
        <Card id="results" v-if="result || errorMessage || isProcessing">
          <CardHeader class="flex flex-row items-start justify-between">
            <div>
              <CardTitle class="text-base">Hasil Analisis</CardTitle>
              <CardDescription class="text-xs mt-1">Respons JSON resmi yang dikembalikan oleh backend FastAPI</CardDescription>
            </div>
            <Badge variant="outline" class="text-cyan-700 bg-cyan-50 border-cyan-200">LANGKAH 02</Badge>
          </CardHeader>

          <CardContent class="space-y-4">
            <!-- ERROR ALERT -->
            <div v-if="errorMessage" class="p-3.5 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs leading-relaxed">
              <strong>Gagal Analisis:</strong> {{ errorMessage }}
            </div>

            <!-- SUCCESS ALERT -->
            <div v-if="result" class="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs leading-relaxed">
              ✔ Prediksi berhasil diproses. Hasil prediksi RUL dan status kondisi mesin ditampilkan pada output di bawah.
            </div>

            <!-- JSON PREVIEW -->
            <div class="space-y-2">
              <div class="flex justify-between items-center text-xs text-slate-500">
                <span>Output API</span>
                <Button v-if="result" variant="outline" size="sm" @click="copyOutput" class="h-8 text-xs">
                  {{ copySuccess ? 'Tersalin!' : 'Salin Hasil' }}
                </Button>
              </div>

              <pre class="bg-slate-900 text-cyan-300 p-4 rounded-xl text-xs font-mono overflow-x-auto leading-relaxed max-h-96">{{ isProcessing ? 'Menghubungi backend FastAPI dan menganalisis dataset...' : JSON.stringify(result || { error: errorMessage }, null, 2) }}</pre>
            </div>
          </CardContent>
        </Card>

        <!-- FOOTER -->
        <footer class="text-center py-6 text-xs text-slate-400">
          PrognoSense © 2026 · Intelligent Machine Health Monitoring System
        </footer>
      </div>
    </main>
  </div>
</template>