<!--
  KondisiView.vue — halaman "Data & kondisi" (Orang 1), versi shadcn-vue
  Rute: /kondisi   Endpoint: GET /api/kondisi   (Kontrak 6)

  Prasyarat (sekali saja, di folder frontend):
    npm i chart.js
    npx shadcn-vue@latest add card table alert button skeleton badge

  Mode mock: VITE_USE_MOCK=true membaca /mock/kondisi.json (taruh di frontend/public/mock/).
  Warna teks, garis grid, dan mode gelap mengikuti tema shadcn (kelas Tailwind), bukan CSS sendiri.
-->
<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const DATA_URL = USE_MOCK ? '/mock/kondisi.json' : '/api/kondisi'

// Palet 6 warna (Okabe-Ito) untuk enam kondisi operasi, aman untuk buta warna.
const WARNA_KONDISI = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00']
const WARNA_TAHAP = { sehat: '#009E73', menurun: '#E69F00', kritis: '#CC3311' }

const status = ref('loading') // loading | error | empty | ok
const errorMsg = ref('')
const data = ref(null)

const rootEl = ref(null)
const scatterEl = ref(null)
const elbowEl = ref(null)
const silEl = ref(null)
const rawEl = ref(null)
const normEl = ref(null)
const umurEl = ref(null)
let charts = []
let pengamatTema = null

// ---------- data turunan ----------
const sampel = computed(() => data.value?.sampel_titik ?? [])
const centroid = computed(() => data.value?.centroid ?? [])
const pemilihanK = computed(() => data.value?.pemilihan_k ?? [])
const sb = computed(() => data.value?.sebelum_sesudah ?? null)
const hasSb = computed(() => !!sb.value && Array.isArray(sb.value.cycle) && sb.value.cycle.length > 0)
const kes = computed(() => data.value?.kesehatan ?? null)
const profil = computed(() => kes.value?.profil ?? [])
const perUmur = computed(() => kes.value?.per_umur ?? [])
const sensorKeys = computed(() =>
  profil.value.length ? Object.keys(profil.value[0]).filter((k) => k !== 'tahap') : []
)

const fmt = (x, d = 2) =>
  Number(x).toLocaleString('id-ID', { minimumFractionDigits: d, maximumFractionDigits: d })

const tiles = computed(() => {
  if (!data.value) return []
  const t = [{ label: 'Kondisi operasi (K)', nilai: String(data.value.k) }]
  if (data.value.silhouette_kondisi != null)
    t.push({ label: 'Silhouette kondisi', nilai: fmt(data.value.silhouette_kondisi, 4) })
  if (kes.value?.silhouette != null)
    t.push({ label: 'Silhouette tahap kesehatan', nilai: fmt(kes.value.silhouette, 2) })
  t.push({ label: 'Titik pada scatter', nilai: sampel.value.length.toLocaleString('id-ID') })
  return t
})

const catatanK = computed(() => {
  const rows = pemilihanK.value
  const k = data.value?.k
  if (!rows.length || k == null) return ''
  const best = rows.reduce((a, b) => (b.silhouette > a.silhouette ? b : a))
  const rk = rows.find((r) => r.k === k)
  const rPrev = rows.find((r) => r.k === k - 1)
  let t = ''
  if (best.k === k) t += `Silhouette tertinggi ada di K = ${k} (${fmt(best.silhouette, 4)}). `
  if (rk && rPrev) {
    t += `WCSS turun dari ${fmt(rPrev.wcss, 0)} (K = ${k - 1}) menjadi ${fmt(rk.wcss, 3)} (K = ${k}); `
    t += 'setelah itu hampir tidak turun lagi.'
  }
  return t
})

const catatanTahap = computed(() => {
  const rows = perUmur.value
  if (!rows.length) return ''
  const pertama = rows.find((r) => r.kritis > 0)
  const akhir = rows[rows.length - 1]
  let t = pertama
    ? `Tahap kritis mulai muncul pada umur ${pertama.persen_umur}% `
    : 'Tahap kritis tidak muncul sama sekali '
  t += `dan mencapai ${fmt(akhir.kritis * 100, 0)}% pada umur ${akhir.persen_umur}%.`
  return t
})

// Warna sel heatmap: merah = di atas rata-rata kondisi, biru = di bawah.
function sel(v) {
  const a = Math.min(Math.abs(v) / 3, 1) * 0.85
  return {
    backgroundColor: v >= 0 ? `rgba(213,94,0,${a})` : `rgba(0,114,178,${a})`,
    color: a > 0.5 ? '#fff' : undefined
  }
}
const namaSensor = (k) => k.replace('_mean10', '')

// ---------- memuat data ----------
async function load() {
  status.value = 'loading'
  errorMsg.value = ''
  destroyCharts()
  try {
    const r = await fetch(DATA_URL)
    if (!r.ok) throw new Error(`server menjawab ${r.status}`)
    const j = await r.json()
    if (!j || !Array.isArray(j.sampel_titik) || j.sampel_titik.length === 0) {
      status.value = 'empty'
      return
    }
    data.value = j
    status.value = 'ok'
    await nextTick()
    buildCharts()
  } catch (e) {
    errorMsg.value = e?.message || 'kesalahan tidak dikenal'
    status.value = 'error'
  }
}

// ---------- warna dari tema shadcn ----------
// Chart.js butuh warna yang sudah jadi. Kelas Tailwind (text-foreground, border-border, ...)
// sudah benar untuk tema terang maupun gelap, jadi nilainya dibaca dari elemen pengukur.
function warnaTema(kelas, properti = 'color') {
  const el = document.createElement('span')
  el.className = `absolute invisible pointer-events-none ${kelas}`
  rootEl.value.appendChild(el)
  const v = getComputedStyle(el)[properti]
  el.remove()
  return v
}

function destroyCharts() {
  charts.forEach((c) => c.destroy())
  charts = []
}
const add = (c) => charts.push(c)

function buildCharts() {
  destroyCharts()
  const teks = warnaTema('text-foreground')
  Chart.defaults.color = warnaTema('text-muted-foreground')
  Chart.defaults.borderColor = warnaTema('border border-border', 'borderTopColor')
  Chart.defaults.font.family = 'inherit'
  const k = data.value.k

  // 1. Scatter set1 vs set2 per kondisi
  if (scatterEl.value) {
    const sets = centroid.value.map((c, i) => ({
      label: `Kondisi ${i} (${fmt(c[0], 0)}; ${fmt(c[1], 2)}; ${fmt(c[2], 0)})`,
      data: sampel.value.filter((p) => p.kondisi === i).map((p) => ({ x: p.set1, y: p.set2 })),
      backgroundColor: WARNA_KONDISI[i % WARNA_KONDISI.length] + 'aa',
      pointRadius: 3
    }))
    sets.push({
      label: 'Centroid',
      data: centroid.value.map((c) => ({ x: c[0], y: c[1] })),
      pointStyle: 'crossRot',
      pointRadius: 9,
      borderWidth: 2,
      borderColor: teks,
      backgroundColor: teks
    })
    add(
      new Chart(scatterEl.value, {
        type: 'scatter',
        data: { datasets: sets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          parsing: false,
          animation: false,
          scales: {
            x: { title: { display: true, text: 'set1 (setting operasional 1)' } },
            y: { title: { display: true, text: 'set2 (setting operasional 2)' } }
          },
          plugins: { legend: { labels: { usePointStyle: true, boxWidth: 8 } } }
        }
      })
    )
  }

  // 2. Elbow (WCSS, skala log) dan 3. Silhouette
  const ks = pemilihanK.value
  const radius = ks.map((r) => (r.k === k ? 7 : 3))
  const garisK = (el, key, label, warna, yOpt) =>
    new Chart(el, {
      type: 'line',
      data: {
        labels: ks.map((r) => r.k),
        datasets: [
          {
            label,
            data: ks.map((r) => r[key]),
            borderColor: warna,
            backgroundColor: warna,
            pointRadius: radius,
            tension: 0.15
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { title: { display: true, text: 'Jumlah cluster (K)' } }, y: yOpt },
        plugins: { legend: { display: false } }
      }
    })
  if (elbowEl.value && ks.length) {
    add(garisK(elbowEl.value, 'wcss', 'WCSS', WARNA_KONDISI[0], {
      type: 'logarithmic',
      title: { display: true, text: 'WCSS (skala log)' }
    }))
  }
  if (silEl.value && ks.length) {
    add(garisK(silEl.value, 'silhouette', 'Silhouette', WARNA_KONDISI[2], {
      min: 0,
      max: 1,
      title: { display: true, text: 'Silhouette' }
    }))
  }

  // 4. Sebelum / sesudah normalisasi
  if (hasSb.value) {
    const garisSb = (el, arr, label, warna, judulY) =>
      new Chart(el, {
        type: 'line',
        data: {
          labels: sb.value.cycle,
          datasets: [{ label, data: arr, borderColor: warna, borderWidth: 1.5, pointRadius: 0 }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: false,
          scales: {
            x: { title: { display: true, text: 'Siklus' }, ticks: { maxTicksLimit: 10 } },
            y: { title: { display: true, text: judulY } }
          },
          plugins: { legend: { display: false } }
        }
      })
    if (rawEl.value)
      add(garisSb(rawEl.value, sb.value.mentah, 'Mentah', WARNA_KONDISI[5], `${sb.value.sensor} (nilai mentah)`))
    if (normEl.value)
      add(garisSb(normEl.value, sb.value.normal, 'Normal', WARNA_KONDISI[0], `${sb.value.sensor} (z-score per kondisi)`))
  }

  // 5. Proporsi tahap terhadap persentase umur
  if (umurEl.value && perUmur.value.length) {
    const urutan = kes.value.urutan ?? ['sehat', 'menurun', 'kritis']
    add(
      new Chart(umurEl.value, {
        type: 'line',
        data: {
          labels: perUmur.value.map((r) => `${r.persen_umur}%`),
          datasets: urutan.map((t) => ({
            label: t,
            data: perUmur.value.map((r) => r[t]),
            borderColor: WARNA_TAHAP[t],
            backgroundColor: WARNA_TAHAP[t] + 'cc',
            fill: true,
            pointRadius: 2,
            tension: 0.2
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { title: { display: true, text: 'Persentase umur mesin (kelompok C)' } },
            y: {
              stacked: true,
              min: 0,
              max: 1,
              title: { display: true, text: 'Proporsi baris' },
              ticks: { callback: (v) => Math.round(v * 100) + '%' }
            }
          },
          plugins: {
            legend: { labels: { usePointStyle: true, boxWidth: 8 } },
            tooltip: {
              callbacks: { label: (c) => `${c.dataset.label}: ${(c.parsed.y * 100).toFixed(0)}%` }
            }
          }
        }
      })
    )
  }
}

onMounted(() => {
  load()
  // Saat tema diganti (kelas "dark" di <html>), warna grafik dibaca ulang.
  pengamatTema = new MutationObserver(() => {
    if (status.value === 'ok') buildCharts()
  })
  pengamatTema.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
})
onBeforeUnmount(() => {
  pengamatTema?.disconnect()
  destroyCharts()
})
</script>

<template>
  <section ref="rootEl" class="relative mx-auto max-w-6xl space-y-4 px-4 py-6">
    <header class="space-y-1">
      <h1 class="text-2xl font-semibold tracking-tight">Data &amp; kondisi</h1>
      <p class="text-sm text-muted-foreground">
        Apakah clustering menemukan kondisi operasi dan tahap kesehatan yang bermakna?
      </p>
    </header>

    <!-- memuat -->
    <div v-if="status === 'loading'" class="space-y-4" role="status" aria-label="Memuat data kondisi">
      <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Skeleton v-for="i in 4" :key="i" class="h-24" />
      </div>
      <Skeleton class="h-96 w-full" />
    </div>

    <!-- gagal -->
    <Alert v-else-if="status === 'error'" variant="destructive">
      <AlertTitle>Gagal memuat data kondisi</AlertTitle>
      <AlertDescription class="space-y-3">
        <p>Server menjawab: {{ errorMsg }}.</p>
        <Button variant="outline" size="sm" @click="load">Coba lagi</Button>
      </AlertDescription>
    </Alert>

    <!-- kosong -->
    <Alert v-else-if="status === 'empty'">
      <AlertTitle>Belum ada data kondisi</AlertTitle>
      <AlertDescription>
        Jalankan notebook 02, lalu salin <code class="font-mono">kondisi.json</code> ke folder
        <code class="font-mono">data/hasil/</code> di server.
      </AlertDescription>
    </Alert>

    <template v-else>
      <div class="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Card v-for="t in tiles" :key="t.label">
          <CardHeader class="space-y-1 p-4">
            <CardDescription>{{ t.label }}</CardDescription>
            <CardTitle class="text-2xl tabular-nums">{{ t.nilai }}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enam kondisi operasi</CardTitle>
          <CardDescription>
            Setiap titik adalah satu baris data (sampel acak). Tanda silang adalah centroid; angka di
            legenda adalah (set1; set2; set3).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="relative h-96">
            <canvas ref="scatterEl" role="img" aria-label="Scatter set1 terhadap set2 berwarna per kondisi"></canvas>
          </div>
        </CardContent>
      </Card>

      <Card v-if="pemilihanK.length">
        <CardHeader>
          <CardTitle>Pemilihan jumlah cluster</CardTitle>
          <CardDescription v-if="catatanK">{{ catatanK }}</CardDescription>
        </CardHeader>
        <CardContent class="grid gap-6 md:grid-cols-2">
          <div class="space-y-2">
            <h3 class="text-sm font-medium text-muted-foreground">Elbow (WCSS)</h3>
            <div class="relative h-72"><canvas ref="elbowEl" role="img" aria-label="Grafik WCSS terhadap K"></canvas></div>
          </div>
          <div class="space-y-2">
            <h3 class="text-sm font-medium text-muted-foreground">Silhouette</h3>
            <div class="relative h-72"><canvas ref="silEl" role="img" aria-label="Grafik silhouette terhadap K"></canvas></div>
          </div>
        </CardContent>
      </Card>

      <Card v-if="hasSb">
        <CardHeader>
          <CardTitle>Sebelum dan sesudah normalisasi</CardTitle>
          <CardDescription>
            Sensor {{ sb.sensor }} pada mesin {{ sb.unit }}. Nilai mentah melompat mengikuti kondisi
            operasi; setelah z-score per kondisi, yang tersisa adalah perubahan akibat kondisi mesin.
          </CardDescription>
        </CardHeader>
        <CardContent class="grid gap-6 md:grid-cols-2">
          <div class="space-y-2">
            <h3 class="text-sm font-medium text-muted-foreground">Mentah</h3>
            <div class="relative h-72"><canvas ref="rawEl" role="img" aria-label="Sensor mentah terhadap siklus"></canvas></div>
          </div>
          <div class="space-y-2">
            <h3 class="text-sm font-medium text-muted-foreground">Ternormalisasi</h3>
            <div class="relative h-72"><canvas ref="normEl" role="img" aria-label="Sensor ternormalisasi terhadap siklus"></canvas></div>
          </div>
        </CardContent>
      </Card>

      <Card v-if="profil.length">
        <CardHeader>
          <CardTitle>Profil tiga tahap kesehatan</CardTitle>
          <CardDescription>
            Rata-rata ternormalisasi 10 siklus terakhir per sensor. Merah = di atas rata-rata kondisi,
            biru = di bawah.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table class="text-xs tabular-nums">
            <TableHeader>
              <TableRow>
                <TableHead>Tahap</TableHead>
                <TableHead v-for="s in sensorKeys" :key="s" class="text-center">{{ namaSensor(s) }}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="p in profil" :key="p.tahap">
                <TableCell>
                  <Badge
                    variant="outline"
                    class="capitalize"
                    :style="{ borderColor: WARNA_TAHAP[p.tahap], color: WARNA_TAHAP[p.tahap] }"
                  >
                    {{ p.tahap }}
                  </Badge>
                </TableCell>
                <TableCell v-for="s in sensorKeys" :key="s" class="text-center" :style="sel(p[s])">
                  {{ fmt(p[s], 2) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card v-if="perUmur.length">
        <CardHeader>
          <CardTitle>Tahap kesehatan menurut umur mesin</CardTitle>
          <CardDescription>
            {{ catatanTahap }}
            <template v-if="kes?.silhouette != null">
              Silhouette tahap ({{ fmt(kes.silhouette, 2) }}) jauh di bawah kondisi operasi: degradasi
              berlangsung bertahap, jadi batas antartahap tidak setegas batas antarkondisi.
            </template>
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div class="relative h-96">
            <canvas ref="umurEl" role="img" aria-label="Proporsi tahap kesehatan terhadap persentase umur"></canvas>
          </div>
        </CardContent>
      </Card>
    </template>
  </section>
</template>