<script setup>
import { computed, onMounted, ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ChartBox from '@/components/ChartBox.vue'
import { getJSON } from '@/api/client'
import { WARNA } from '@/lib/warna'

const d = ref(null)
const galat = ref('')
const rasio = ref(100)
onMounted(async () => { try { d.value = await getJSON('/api/evaluasi') } catch (e) { galat.value = e.message } })

const sebar = computed(() => ({
  type: 'scatter',
  data: { datasets: [
    { label: 'mesin test', data: d.value.rul.sebar.map((s) => ({ x: s.rul_aktual, y: s.rul_pred })), backgroundColor: WARNA[0] + 'aa', pointRadius: 3 },
    { label: 'prediksi sempurna', type: 'line', data: [{ x: 0, y: 0 }, { x: 125, y: 125 }], borderColor: '#0b0b0b', borderDash: [5, 4], pointRadius: 0 },
  ] },
  options: { scales: { x: { type: 'linear', title: { display: true, text: 'RUL aktual (dipotong 125)' } }, y: { title: { display: true, text: 'RUL prediksi' } } } },
}))
const importance = computed(() => ({
  type: 'bar',
  data: { labels: d.value.rul.importance.map((i) => i.fitur), datasets: [{ data: d.value.rul.importance.map((i) => +(i.nilai * 100).toFixed(1)), backgroundColor: WARNA[0] }] },
  options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { title: { display: true, text: '% gain' } } } },
}))
const kurva = computed(() => ({
  type: 'line',
  data: { labels: d.value.rl.kurva_reward.map((k) => k.episode), datasets: [{ label: 'reward rata-rata per 100 episode', data: d.value.rl.kurva_reward.map((k) => k.rata2), borderColor: WARNA[2], pointRadius: 0, borderWidth: 2 }] },
  options: { scales: { x: { title: { display: true, text: 'episode' }, ticks: { maxTicksLimit: 10 } }, y: { title: { display: true, text: 'reward' } } } },
}))
const strategi = computed(() => d.value.rl.strategi.filter((s) => s.rasio === rasio.value))
const param = (p) => Object.entries(p || {}).map(([k, v]) => `${k} = ${v}`).join(', ')
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Seberapa baik model RUL dan agen dibanding cara sederhana?</h1>
      <p class="text-sm text-slate-500 mt-1">Supervised: model RUL dipilih di kelompok B, dilaporkan di test resmi. Reinforcement: agen dilatih di B, diuji di C.</p>
    </div>
    <p v-if="galat" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">{{ galat }}</p>
    <p v-else-if="!d" class="text-sm text-slate-500">Memuat…</p>
    <template v-else>
      <Card>
        <CardHeader><CardTitle class="text-base">Perbandingan model RUL</CardTitle>
          <CardDescription class="text-xs">Terpilih: <b>{{ d.rul.terpilih }}</b> (RMSE terkecil di B). Test dinilai pada {{ d.rul.dinilai_pada }}.</CardDescription></CardHeader>
        <CardContent class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr class="text-left text-xs text-slate-500 border-b"><th class="py-2">Model</th><th class="text-right">RMSE B</th><th class="text-right">MAE B</th><th class="text-right">RMSE test</th><th class="text-right">MAE test</th><th class="text-right">Latih (s)</th></tr></thead>
            <tbody>
              <tr v-for="m in d.rul.model" :key="m.nama" class="border-b last:border-0" :class="m.nama === d.rul.terpilih ? 'font-semibold bg-cyan-50/60' : ''">
                <td class="py-2">{{ m.nama }}</td><td class="text-right tabular-nums">{{ m.rmse_b }}</td><td class="text-right tabular-nums">{{ m.mae_b }}</td>
                <td class="text-right tabular-nums">{{ m.rmse }}</td><td class="text-right tabular-nums">{{ m.mae }}</td><td class="text-right tabular-nums">{{ m.detik_latih }}</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
      <div class="grid md:grid-cols-2 gap-6">
        <Card><CardHeader><CardTitle class="text-base">Prediksi vs aktual (test resmi)</CardTitle>
          <CardDescription class="text-xs">Di atas garis: terlalu optimis. Di bawah: terlalu pesimis.</CardDescription></CardHeader>
          <CardContent><ChartBox :config="sebar" :height="300" /></CardContent></Card>
        <Card><CardHeader><CardTitle class="text-base">10 fitur terpenting</CardTitle>
          <CardDescription class="text-xs">Yang paling dipakai model, bukan penyebab kerusakan.</CardDescription></CardHeader>
          <CardContent><ChartBox :config="importance" :height="300" /></CardContent></Card>
      </div>
      <Card>
        <CardHeader class="flex flex-row items-center justify-between gap-3">
          <div><CardTitle class="text-base">Perbandingan strategi perawatan (kelompok C)</CardTitle>
            <CardDescription class="text-xs mt-1">{{ d.rl.catatan }}</CardDescription></div>
          <select v-model.number="rasio" class="border border-slate-300 rounded-md px-2 py-1.5 bg-white text-xs">
            <option :value="50">rasio 50 : 10</option><option :value="100">rasio 100 : 10</option><option :value="200">rasio 200 : 10</option>
          </select>
        </CardHeader>
        <CardContent class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr class="text-left text-xs text-slate-500 border-b"><th class="py-2">Strategi</th><th>Parameter</th><th class="text-right">Gagal %</th><th class="text-right">Siklus terbuang</th><th class="text-right">Siklus produktif</th><th class="text-right">Biaya</th></tr></thead>
            <tbody>
              <tr v-for="s in strategi" :key="s.nama" class="border-b last:border-0" :class="s.nama.startsWith('Agen') ? 'font-semibold bg-cyan-50/60' : ''">
                <td class="py-2">{{ s.nama }}</td><td class="text-xs text-slate-500">{{ param(s.parameter) }}</td>
                <td class="text-right tabular-nums">{{ s.gagal_pct }}</td><td class="text-right tabular-nums">{{ s.siklus_terbuang ?? '—' }}</td>
                <td class="text-right tabular-nums">{{ s.siklus_produktif }}</td><td class="text-right tabular-nums">{{ s.biaya }}</td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
      <div class="grid md:grid-cols-2 gap-6">
        <Card><CardHeader><CardTitle class="text-base">Kurva belajar Q-Learning (rasio 100)</CardTitle></CardHeader>
          <CardContent><ChartBox :config="kurva" :height="260" /></CardContent></Card>
        <Card><CardHeader><CardTitle class="text-base">Policy 18 state (rasio 100)</CardTitle></CardHeader>
          <CardContent class="overflow-y-auto max-h-[300px]">
            <table class="w-full text-xs">
              <thead><tr class="text-left text-slate-500 border-b"><th class="py-1.5">State (bin RUL · tahap)</th><th>Aksi</th><th class="text-right">Q lanjut</th><th class="text-right">Q rawat</th></tr></thead>
              <tbody><tr v-for="p in d.rl.policy" :key="p.state" class="border-b last:border-0">
                <td class="py-1.5">{{ p.state }}</td><td><Badge :variant="p.aksi === 'rawat' ? 'destructive' : 'outline'">{{ p.aksi }}</Badge></td>
                <td class="text-right tabular-nums">{{ p.q_lanjut }}</td><td class="text-right tabular-nums">{{ p.q_rawat }}</td></tr></tbody>
            </table>
          </CardContent></Card>
      </div>
    </template>
  </div>
</template>
