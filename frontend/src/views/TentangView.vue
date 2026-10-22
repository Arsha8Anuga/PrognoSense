<script setup>
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
defineProps({ health: Object })
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <h1 class="text-2xl font-bold tracking-tight">Data apa, metode apa, dan apa batasannya?</h1>
    <Card>
      <CardHeader><CardTitle class="text-base">Data</CardTitle></CardHeader>
      <CardContent class="text-sm text-slate-700 space-y-2 leading-relaxed">
        <p>NASA C-MAPSS FD002 + FD004: simulasi mesin turbofan yang dijalankan sampai rusak, 509 mesin train (115.008 baris), enam kondisi operasi, dua mode kerusakan (HPC dan fan, yang kedua hanya di FD004).</p>
        <p>Mesin dibagi per mesin dengan seed 42: <b>A</b> 60% untuk melatih model, <b>B</b> 20% untuk memilih model dan melatih agen, <b>C</b> 20% untuk evaluasi akhir dan dasbor. RMSE model RUL dilaporkan pada test resmi NASA.</p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader><CardTitle class="text-base">Alur tiga paradigma</CardTitle></CardHeader>
      <CardContent class="text-sm text-slate-700 space-y-2 leading-relaxed">
        <p><b>Unsupervised.</b> K-Means mengelompokkan setting operasional menjadi 6 kondisi, lalu sensor dinormalisasi per kondisi. K-Means kedua membagi rata-rata sensor menjadi 3 tahap kesehatan.</p>
        <p><b>Supervised.</b> LightGBM menebak sisa umur (RUL, dipotong di 125) dari 43 fitur jendela 10 siklus. Dipilih dari lima kandidat berdasarkan RMSE di kelompok B.</p>
        <p><b>Reinforcement.</b> Q-Learning memutuskan lanjut atau rawat dari state bin RUL × tahap (18 state), dibandingkan dengan aturan ambang, rawat periodik, jalan sampai rusak, dan oracle.</p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader><CardTitle class="text-base">Keterbatasan</CardTitle></CardHeader>
      <CardContent class="text-sm text-slate-700 space-y-2 leading-relaxed">
        <p>Data simulasi, bukan data pabrik. Degradasi diputar ulang dari data: agen hanya memilih kapan lintasan dihentikan, tidak mengubah keausan. Rasio biaya gagal : rawat adalah asumsi.</p>
        <p>RUL di atas 125 hanya bisa ditebak sebagai "≥ 125". Tahap "kritis" lebih mewakili mode kerusakan fan di FD004 daripada tingkat keparahan. Enam bin RUL terlalu kasar sehingga rasio 200 menghasilkan kebijakan yang sama dengan rasio 100.</p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader><CardTitle class="text-base">Status</CardTitle></CardHeader>
      <CardContent class="text-sm">
        <p v-if="health">Model <b>{{ health.model_version }}</b>, dimuat {{ health.dimuat }}.</p>
        <p v-else class="text-red-600">Backend tidak dapat dihubungi.</p>
      </CardContent>
    </Card>
  </div>
</template>
