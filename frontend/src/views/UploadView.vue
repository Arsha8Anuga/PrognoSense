<script setup>
import { ref } from 'vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { uploadCSV } from '@/api/client'
import { WARNA_TAHAP } from '@/lib/warna'

const file = ref(null)
const rasio = ref(100)
const sampaiRusak = ref(false)
const proses = ref(false)
const hasil = ref(null)
const galat = ref(null)

const pilih = (e) => { file.value = e.target.files[0] || null; hasil.value = null; galat.value = null }
const jalankan = async () => {
  proses.value = true; hasil.value = null; galat.value = null
  try { hasil.value = await uploadCSV(file.value, rasio.value, sampaiRusak.value) }
  catch (e) { galat.value = { pesan: e.message, detail: e.detail || [] } }
  finally { proses.value = false }
}
</script>

<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold tracking-tight">Apa rekomendasi untuk data mesin saya, atau kenapa ditolak?</h1>
      <p class="text-sm text-slate-500 mt-1">CSV dengan header <code class="text-xs">unit, cycle, set1–set3, s1–s21</code>, atau file teks NASA tanpa header. Maksimal 20 MB.</p>
    </div>

    <Card>
      <CardContent class="pt-6 space-y-4">
        <label class="block border-2 border-dashed border-slate-200 hover:border-cyan-400 rounded-xl p-8 text-center cursor-pointer">
          <input type="file" accept=".csv,.txt" class="hidden" @change="pilih" />
          <div class="text-sm font-semibold">{{ file ? file.name : 'Klik untuk memilih file .csv atau .txt' }}</div>
          <div v-if="file" class="text-xs text-slate-500 mt-1">{{ (file.size / 1024).toFixed(1) }} KB</div>
        </label>
        <div class="flex flex-wrap items-center gap-4 text-sm">
          <label class="flex items-center gap-2">Rasio biaya
            <select v-model.number="rasio" class="border border-slate-300 rounded-md px-2 py-1 bg-white">
              <option :value="50">50 : 10</option><option :value="100">100 : 10</option><option :value="200">200 : 10</option>
            </select></label>
          <label class="flex items-center gap-2"><input type="checkbox" v-model="sampaiRusak" /> Lintasan sampai rusak</label>
          <Button class="ml-auto bg-cyan-600 hover:bg-cyan-700 text-white" :disabled="!file || proses" @click="jalankan">
            {{ proses ? 'Memproses…' : 'Jalankan prediksi' }}</Button>
        </div>
      </CardContent>
    </Card>

    <Card v-if="galat">
      <CardHeader><CardTitle class="text-base text-red-700">File ditolak</CardTitle><CardDescription>{{ galat.pesan }}</CardDescription></CardHeader>
      <CardContent v-if="galat.detail.length">
        <table class="w-full text-sm">
          <thead><tr class="text-left text-xs text-slate-500 border-b"><th class="py-2">Kode</th><th>Unit</th><th>Baris</th><th>Kolom</th><th>Pesan</th></tr></thead>
          <tbody><tr v-for="(e, i) in galat.detail" :key="i" class="border-b last:border-0">
            <td class="py-2"><Badge variant="destructive">{{ e.kode }}</Badge></td><td>{{ e.unit ?? '—' }}</td>
            <td>{{ e.baris ?? '—' }}</td><td>{{ e.kolom ?? '—' }}</td><td class="text-slate-600">{{ e.pesan }}</td></tr></tbody>
        </table>
      </CardContent>
    </Card>

    <template v-if="hasil">
      <Card>
        <CardHeader><CardTitle class="text-base">Hasil · {{ hasil.mesin_diterima }} mesin diterima, {{ hasil.mesin_ditolak }} ditolak</CardTitle>
          <CardDescription class="text-xs">Model {{ hasil.model_version }} · rasio {{ hasil.rasio }} : 10 · prediksi untuk siklus terakhir setiap mesin
            <template v-if="hasil.layak_training"> · ditandai layak untuk training (belum dipakai)</template></CardDescription></CardHeader>
        <CardContent class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead><tr class="text-left text-xs text-slate-500 border-b"><th class="py-2">Unit</th><th>Siklus terakhir</th><th>Kondisi</th><th>Tahap</th><th class="text-right">RUL prediksi</th><th class="text-right">Q lanjut</th><th class="text-right">Q rawat</th><th>Aksi</th></tr></thead>
            <tbody><tr v-for="m in hasil.hasil" :key="m.unit" class="border-b last:border-0">
              <td class="py-2 font-medium">{{ m.unit }}</td><td class="tabular-nums">{{ m.siklus_terakhir }}</td><td>{{ m.kondisi }}</td>
              <td><span class="inline-flex items-center gap-1.5"><span class="w-2 h-2 rounded-full" :style="{ background: WARNA_TAHAP[m.tahap] }"></span>{{ m.tahap }}</span></td>
              <td class="text-right tabular-nums font-semibold">{{ m.rul_pred }}</td>
              <td class="text-right tabular-nums">{{ m.q?.lanjut ?? '—' }}</td><td class="text-right tabular-nums">{{ m.q?.rawat ?? '—' }}</td>
              <td><Badge v-if="m.aksi" :variant="m.aksi === 'rawat' ? 'destructive' : 'outline'">{{ m.aksi }}</Badge><span v-else>—</span></td></tr></tbody>
          </table>
        </CardContent>
      </Card>
      <Card v-if="hasil.peringatan.length">
        <CardHeader><CardTitle class="text-base">Mesin yang ditolak</CardTitle></CardHeader>
        <CardContent><ul class="text-sm space-y-1.5">
          <li v-for="(p, i) in hasil.peringatan" :key="i"><Badge variant="outline">{{ p.kode }}</Badge> <span class="text-slate-600">{{ p.pesan }}</span></li>
        </ul></CardContent>
      </Card>
    </template>
  </div>
</template>
