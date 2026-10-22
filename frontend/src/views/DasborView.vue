<script setup>
import { computed, ref, watch } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getJSON } from '@/api/client'
import { WARNA_TAHAP } from '@/lib/warna'

const rasio = ref(100)
const data = ref(null)
const galat = ref('')
const filter = ref('semua')

watch(rasio, async (r) => {
  galat.value = ''
  try { data.value = await getJSON(`/api/armada?rasio=${r}`) } catch (e) { galat.value = e.message; data.value = null }
}, { immediate: true })

const buka = (u) => { location.hash = `#/mesin/${u}` }
const mesin = computed(() => (data.value?.mesin || []).filter((m) => filter.value === 'semua' || m.tahap === filter.value))
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-3">
      <div>
        <h1 class="text-2xl font-bold tracking-tight">Mesin mana yang harus didatangi lebih dulu?</h1>
        <p class="text-sm text-slate-500 mt-1">102 mesin kelompok C, masing-masing dipotong di titik acak 50–95% umurnya, seolah sedang beroperasi.</p>
      </div>
      <label class="text-xs text-slate-600 flex items-center gap-2">Rasio biaya gagal : rawat
        <select v-model.number="rasio" class="border border-slate-300 rounded-md px-2 py-1.5 bg-white text-sm">
          <option :value="50">50 : 10</option><option :value="100">100 : 10</option><option :value="200">200 : 10</option>
        </select>
      </label>
    </div>

    <p v-if="galat" class="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">Gagal memuat: {{ galat }}</p>
    <p v-else-if="!data" class="text-sm text-slate-500">Memuat…</p>

    <template v-else>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card><CardHeader class="pb-1"><CardDescription>Total mesin</CardDescription></CardHeader>
          <CardContent class="text-3xl font-extrabold">{{ data.ringkasan.total }}</CardContent></Card>
        <Card><CardHeader class="pb-1"><CardDescription>Rawat sekarang</CardDescription></CardHeader>
          <CardContent class="text-3xl font-extrabold text-red-600">{{ data.ringkasan.rawat_sekarang }}</CardContent></Card>
        <Card><CardHeader class="pb-1"><CardDescription>Per tahap kesehatan</CardDescription></CardHeader>
          <CardContent class="text-sm space-y-0.5">
            <div v-for="(n, t) in data.ringkasan.per_tahap" :key="t" class="flex justify-between">
              <span class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" :style="{ background: WARNA_TAHAP[t] }"></span>{{ t }}</span><b>{{ n }}</b>
            </div>
          </CardContent></Card>
        <Card><CardHeader class="pb-1"><CardDescription>Rata-rata RUL prediksi</CardDescription></CardHeader>
          <CardContent class="text-3xl font-extrabold">{{ data.ringkasan.rata2_rul_pred }} <span class="text-sm font-normal text-slate-500">siklus</span></CardContent></Card>
      </div>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between gap-3">
          <div>
            <CardTitle class="text-base">Armada, urut dari RUL prediksi terkecil</CardTitle>
            <CardDescription class="text-xs mt-1">Klik baris untuk melihat kenapa agen memutuskan begitu.</CardDescription>
          </div>
          <select v-model="filter" class="border border-slate-300 rounded-md px-2 py-1.5 bg-white text-xs">
            <option value="semua">Semua tahap</option><option>sehat</option><option>menurun</option><option>kritis</option>
          </select>
        </CardHeader>
        <CardContent class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr class="text-left text-xs text-slate-500 border-b">
              <th class="py-2 pr-3">Unit</th><th class="pr-3">Siklus</th><th class="pr-3">Kondisi</th><th class="pr-3">Tahap</th>
              <th class="pr-3 text-right">RUL prediksi</th><th class="pr-3 text-right">RUL aktual</th><th>Aksi agen</th></tr></thead>
            <tbody>
              <tr v-for="m in mesin" :key="m.unit" class="border-b last:border-0 hover:bg-slate-50 cursor-pointer"
                  @click="buka(m.unit)">
                <td class="py-2 pr-3 font-medium text-cyan-700">{{ m.unit }}</td>
                <td class="pr-3 tabular-nums">{{ m.siklus }}</td>
                <td class="pr-3">{{ m.kondisi }}</td>
                <td class="pr-3"><span class="inline-flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" :style="{ background: WARNA_TAHAP[m.tahap] }"></span>{{ m.tahap }}</span></td>
                <td class="pr-3 text-right tabular-nums font-semibold">{{ m.rul_pred }}</td>
                <td class="pr-3 text-right tabular-nums text-slate-500">{{ m.rul_aktual }}</td>
                <td>
                  <Badge :variant="m.aksi === 'rawat' ? 'destructive' : 'outline'">{{ m.aksi }}</Badge>
                  <span v-if="m.terlambat" class="ml-2 text-[11px] text-red-600">seharusnya lebih awal</span>
                </td>
              </tr>
            </tbody>
          </table>
        </CardContent>
      </Card>
    </template>
  </div>
</template>
