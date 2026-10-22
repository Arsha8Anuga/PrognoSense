<script setup>
import { computed, ref, watch } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import ChartBox from '@/components/ChartBox.vue'
import { getJSON } from '@/api/client'
import { WARNA, WARNA_TAHAP } from '@/lib/warna'

const props = defineProps({ unit: String })
const rasio = ref(100)
const data = ref(null)
const galat = ref('')
const idx = ref(0)

watch(rasio, async (r) => {
  galat.value = ''
  try {
    data.value = await getJSON(`/api/mesin/${encodeURIComponent(props.unit)}?rasio=${r}`)
    const k = data.value.keputusan.siklus_rawat
    idx.value = k ? k - 1 : data.value.siklus.length - 1
  } catch (e) { galat.value = e.message; data.value = null }
}, { immediate: true })

const siklus = computed(() => data.value?.siklus || [])
const sekarang = computed(() => siklus.value[idx.value])
const label = computed(() => siklus.value.map((s) => s.cycle))

// garis tegak: siklus saat ini (slider), siklus rawat agen, siklus rusak
const penanda = computed(() => {
  const d = data.value
  if (!d) return []
  const g = [{ x: sekarang.value?.cycle, warna: '#0b0b0b', teks: 'siklus dipilih' }]
  if (d.keputusan.siklus_rawat) g.push({ x: d.keputusan.siklus_rawat, warna: WARNA[0], teks: 'agen merawat' })
  g.push({ x: d.umur_aktual, warna: '#e34948', teks: 'rusak' })
  return g
})
const pluginPenanda = computed(() => ({
  id: 'penanda',
  afterDatasetsDraw(chart) {
    const { ctx, chartArea: a, scales: { x } } = chart
    penanda.value.forEach((p) => {
      const px = x.getPixelForValue(label.value.indexOf(p.x))
      if (px < a.left || px > a.right) return
      ctx.save(); ctx.strokeStyle = p.warna; ctx.setLineDash([4, 3]); ctx.beginPath()
      ctx.moveTo(px, a.top); ctx.lineTo(px, a.bottom); ctx.stroke(); ctx.restore()
    })
  },
}))

const opsi = (yJudul) => ({
  interaction: { mode: 'index', intersect: false },
  elements: { point: { radius: 0 } },
  scales: { x: { title: { display: true, text: 'siklus' }, ticks: { maxTicksLimit: 12 } }, y: { title: { display: true, text: yJudul } } },
})

const grafikSensor = computed(() => ({
  type: 'line',
  data: { labels: label.value, datasets: data.value.sensor_ditampilkan.map((s, i) => ({
    label: s, data: siklus.value.map((c) => c.sensor[s]), borderColor: WARNA[i], borderWidth: 1.5 })) },
  options: opsi('z (ternormalisasi)'),
  plugins: [pluginPenanda.value],
}))
const grafikRul = computed(() => ({
  type: 'line',
  data: { labels: label.value, datasets: [
    { label: 'RUL prediksi', data: siklus.value.map((c) => c.rul_pred), borderColor: WARNA[0], borderWidth: 2 },
    { label: 'RUL aktual (dipotong 125)', data: siklus.value.map((c) => c.rul_aktual), borderColor: '#52514e', borderDash: [5, 4], borderWidth: 1.5 },
  ] },
  options: opsi('siklus tersisa'),
  plugins: [pluginPenanda.value],
}))
const pitaTahap = computed(() => siklus.value.map((c) => WARNA_TAHAP[c.tahap]))
const qMaks = computed(() => Math.max(1, ...siklus.value.flatMap((c) => [Math.abs(c.q.lanjut), Math.abs(c.q.rawat)])))
</script>

<template>
  <div class="space-y-6">
    <a href="#/" class="text-xs text-cyan-700">← kembali ke Dasbor</a>
    <p v-if="galat" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">{{ galat }}</p>
    <p v-else-if="!data" class="text-sm text-slate-500">Memuat…</p>

    <template v-else>
      <div class="flex flex-col md:flex-row md:items-end justify-between gap-3">
        <div>
          <h1 class="text-2xl font-bold tracking-tight">{{ data.unit }}</h1>
          <p class="text-sm text-slate-500 mt-1">
            Umur sebenarnya {{ data.umur_aktual }} siklus · kondisi dominan {{ data.kondisi_dominan }} ·
            <template v-if="data.keputusan.gagal"><b class="text-red-600">agen membiarkan mesin rusak</b></template>
            <template v-else>agen merawat di siklus <b>{{ data.keputusan.siklus_rawat }}</b>,
              <b>{{ data.keputusan.rul_aktual_saat_rawat }}</b> siklus sebelum rusak</template>
          </p>
        </div>
        <select v-model.number="rasio" class="border border-slate-300 rounded-md px-2 py-1.5 bg-white text-sm w-fit">
          <option :value="50">rasio 50 : 10</option><option :value="100">rasio 100 : 10</option><option :value="200">rasio 200 : 10</option>
        </select>
      </div>

      <Card>
        <CardHeader><CardTitle class="text-base">Geser siklus</CardTitle>
          <CardDescription class="text-xs">Q-value adalah perkiraan agen tentang total reward ke depan untuk setiap aksi. Aksi dengan Q lebih besar yang dipilih.</CardDescription></CardHeader>
        <CardContent class="space-y-4">
          <input type="range" min="0" :max="siklus.length - 1" v-model.number="idx" class="w-full accent-cyan-600" />
          <div class="grid md:grid-cols-4 gap-4 text-sm">
            <div><div class="text-xs text-slate-500">Siklus</div><b class="text-xl">{{ sekarang.cycle }}</b></div>
            <div><div class="text-xs text-slate-500">RUL prediksi / aktual</div><b class="text-xl">{{ sekarang.rul_pred }}</b> / {{ sekarang.rul_aktual }}</div>
            <div><div class="text-xs text-slate-500">Tahap · kondisi</div>
              <span class="inline-flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" :style="{ background: WARNA_TAHAP[sekarang.tahap] }"></span>{{ sekarang.tahap }}</span> · {{ sekarang.kondisi }}</div>
            <div><div class="text-xs text-slate-500">Aksi agen</div><Badge :variant="sekarang.aksi === 'rawat' ? 'destructive' : 'outline'">{{ sekarang.aksi }}</Badge></div>
          </div>
          <div class="space-y-1.5 text-xs">
            <div v-for="a in ['lanjut', 'rawat']" :key="a" class="flex items-center gap-3">
              <span class="w-12 text-slate-600">{{ a }}</span>
              <div class="flex-1 h-4 bg-slate-100 rounded relative">
                <div class="h-4 rounded" :style="{ width: (Math.abs(sekarang.q[a]) / qMaks * 100) + '%', background: a === 'rawat' ? '#e34948' : '#2a78d6', opacity: sekarang.q[a] < 0 ? 0.45 : 1 }"></div>
              </div>
              <span class="w-14 text-right tabular-nums">{{ sekarang.q[a] }}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle class="text-base">RUL prediksi vs aktual</CardTitle>
          <CardDescription class="text-xs">Garis tegak: hitam = siklus dipilih, biru = agen merawat, merah = mesin rusak.</CardDescription></CardHeader>
        <CardContent><ChartBox :config="grafikRul" /></CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle class="text-base">Sensor ternormalisasi dan tahap kesehatan</CardTitle></CardHeader>
        <CardContent class="space-y-2">
          <ChartBox :config="grafikSensor" />
          <div class="flex h-3 rounded overflow-hidden"><div v-for="(w, i) in pitaTahap" :key="i" class="flex-1" :style="{ background: w }"></div></div>
          <div class="flex gap-4 text-[11px] text-slate-500">
            <span v-for="(w, t) in WARNA_TAHAP" :key="t" class="flex items-center gap-1"><span class="w-2 h-2 rounded-full" :style="{ background: w }"></span>{{ t }}</span>
          </div>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
