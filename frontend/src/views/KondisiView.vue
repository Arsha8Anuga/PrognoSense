<script setup>
import { computed, onMounted, ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import ChartBox from '@/components/ChartBox.vue'
import { getJSON } from '@/api/client'
import { WARNA, WARNA_TAHAP } from '@/lib/warna'

const d = ref(null)
const galat = ref('')
onMounted(async () => { try { d.value = await getJSON('/api/kondisi') } catch (e) { galat.value = e.message } })

const scatter = computed(() => ({
  type: 'scatter',
  data: { datasets: [...Array(d.value.k).keys()].map((k) => ({
    label: `kondisi ${k}`, backgroundColor: WARNA[k], pointRadius: 4,
    data: d.value.sampel_titik.filter((t) => t.kondisi === k).map((t) => ({ x: t.set1, y: t.set2 })) })) },
  options: { scales: { x: { title: { display: true, text: 'set1 (ketinggian)' } }, y: { title: { display: true, text: 'set2 (Mach)' } } } },
}))
const garisK = (kunci, judul, warna, log) => ({
  type: 'line',
  data: { labels: d.value.pemilihan_k.map((p) => p.k), datasets: [{ label: judul, data: d.value.pemilihan_k.map((p) => p[kunci]), borderColor: warna, backgroundColor: warna, pointRadius: 4 }] },
  options: { plugins: { legend: { display: false } }, scales: { x: { title: { display: true, text: 'K' } }, y: { type: log ? 'logarithmic' : 'linear', title: { display: true, text: judul } } } },
})
const wcss = computed(() => garisK('wcss', 'WCSS (skala log)', WARNA[0], true))
const sil = computed(() => garisK('silhouette', 'Silhouette', WARNA[1], false))
const sebelumSesudah = computed(() => {
  const s = d.value.sebelum_sesudah
  const o = (t) => ({ elements: { point: { radius: 0 } }, plugins: { legend: { display: false } }, scales: { x: { ticks: { maxTicksLimit: 10 }, title: { display: true, text: 'siklus' } }, y: { title: { display: true, text: t } } } })
  return [
    { type: 'line', data: { labels: s.cycle, datasets: [{ data: s.mentah, borderColor: '#52514e', borderWidth: 1 }] }, options: o(`${s.sensor} mentah`) },
    { type: 'line', data: { labels: s.cycle, datasets: [{ data: s.normal, borderColor: WARNA[0], borderWidth: 1 }] }, options: o(`${s.sensor} z per kondisi`) },
  ]
})
const perUmur = computed(() => {
  const p = d.value.kesehatan.per_umur
  return {
    type: 'bar',
    data: { labels: p.map((r) => `${r.persen_umur}%`), datasets: d.value.kesehatan.urutan.map((t) => ({ label: t, data: p.map((r) => r[t]), backgroundColor: WARNA_TAHAP[t] })) },
    options: { scales: { x: { stacked: true, title: { display: true, text: '% umur mesin (kelompok C)' } }, y: { stacked: true, max: 1, title: { display: true, text: 'proporsi' } } } },
  }
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Apakah clustering menemukan kondisi dan tahap yang bermakna?</h1>
      <p class="text-sm text-slate-500 mt-1">Paradigma unsupervised: K-Means kondisi operasi (K = 6) dan tahap kesehatan (K = 3), dilatih di kelompok A.</p>
    </div>
    <p v-if="galat" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">{{ galat }}</p>
    <p v-else-if="!d" class="text-sm text-slate-500">Memuat…</p>
    <template v-else>
      <Card>
        <CardHeader><CardTitle class="text-base">Enam kondisi operasi</CardTitle>
          <CardDescription class="text-xs">2.000 baris acak. Setiap titik warna adalah ratusan baris yang bertumpuk: setting operasional bersifat diskrit.</CardDescription></CardHeader>
        <CardContent><ChartBox :config="scatter" :height="300" /></CardContent>
      </Card>
      <div class="grid md:grid-cols-2 gap-6">
        <Card><CardHeader><CardTitle class="text-base">Elbow</CardTitle><CardDescription class="text-xs">WCSS jatuh tebing tepat di K = 6.</CardDescription></CardHeader>
          <CardContent><ChartBox :config="wcss" :height="220" /></CardContent></Card>
        <Card><CardHeader><CardTitle class="text-base">Silhouette</CardTitle>
          <CardDescription class="text-xs">Puncak di K = 6 ({{ d.silhouette_kondisi?.toFixed(4) }}).</CardDescription></CardHeader>
          <CardContent><ChartBox :config="sil" :height="220" /></CardContent></Card>
      </div>
      <Card>
        <CardHeader><CardTitle class="text-base">Sebelum dan sesudah normalisasi · {{ d.sebelum_sesudah.unit }}</CardTitle>
          <CardDescription class="text-xs">Nilai mentah melompat mengikuti kondisi; setelah z-score per kondisi, tren keausan muncul.</CardDescription></CardHeader>
        <CardContent class="grid md:grid-cols-2 gap-4">
          <ChartBox :config="sebelumSesudah[0]" :height="220" /><ChartBox :config="sebelumSesudah[1]" :height="220" />
        </CardContent>
      </Card>
      <Card>
        <CardHeader><CardTitle class="text-base">Tahap kesehatan terhadap umur mesin</CardTitle>
          <CardDescription class="text-xs">Silhouette {{ d.kesehatan.silhouette.toFixed(2) }}: keausan bertahap, batas tahap kabur.
            Catatan: "kritis" hanya muncul di FD004 dan sensornya bergerak berlawanan dengan "menurun", sehingga lebih mewakili mode kerusakan fan daripada tingkat keparahan.</CardDescription></CardHeader>
        <CardContent><ChartBox :config="perUmur" :height="280" /></CardContent>
      </Card>
    </template>
  </div>
</template>
