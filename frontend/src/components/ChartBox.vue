<script setup>
// Pembungkus Chart.js: cukup kirim objek konfigurasi; grafik digambar ulang saat konfigurasi berubah.
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({ config: { type: Object, required: true }, height: { type: Number, default: 260 } })
const kanvas = ref(null)
let chart = null

const gambar = () => {
  chart?.destroy()
  chart = new Chart(kanvas.value, { ...props.config, options: { responsive: true, maintainAspectRatio: false, animation: false, ...props.config.options } })
}
onMounted(gambar)
watch(() => props.config, gambar)
onBeforeUnmount(() => chart?.destroy())
</script>

<template>
  <div :style="{ height: height + 'px' }"><canvas ref="kanvas" /></div>
</template>
