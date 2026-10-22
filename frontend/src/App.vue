<script setup>
import { computed, onMounted, ref } from 'vue'
import { Badge } from '@/components/ui/badge'
import { getHealthStatus } from '@/api/client'
import DasborView from '@/views/DasborView.vue'
import MesinView from '@/views/MesinView.vue'
import KondisiView from '@/views/KondisiView.vue'
import EvaluasiView from '@/views/EvaluasiView.vue'
import UploadView from '@/views/UploadView.vue'
import TentangView from '@/views/TentangView.vue'

// Rute berbasis hash: #/, #/mesin/FD004_17, #/kondisi, #/evaluasi, #/upload, #/tentang
const hash = ref(location.hash || '#/')
window.addEventListener('hashchange', () => { hash.value = location.hash || '#/'; window.scrollTo(0, 0) })

const MENU = [
  { href: '#/', label: 'Dasbor', ikon: '▦' },
  { href: '#/kondisi', label: 'Data & kondisi', ikon: '◎' },
  { href: '#/evaluasi', label: 'Evaluasi', ikon: '▤' },
  { href: '#/upload', label: 'Upload CSV', ikon: '⇧' },
  { href: '#/tentang', label: 'Tentang', ikon: 'ⓘ' },
]

const halaman = computed(() => {
  const h = hash.value
  if (h.startsWith('#/mesin/')) return { komp: MesinView, judul: 'Detail mesin', props: { unit: decodeURIComponent(h.slice(8)) } }
  const peta = { '#/kondisi': [KondisiView, 'Data & kondisi'], '#/evaluasi': [EvaluasiView, 'Evaluasi'],
                 '#/upload': [UploadView, 'Upload CSV'], '#/tentang': [TentangView, 'Tentang'] }
  const [komp, judul] = peta[h] || [DasborView, 'Dasbor']
  return { komp, judul, props: {} }
})
const aktif = (href) => (href === '#/' ? hash.value === '#/' || hash.value.startsWith('#/mesin/') : hash.value === href)

const health = ref(null)
onMounted(async () => { try { health.value = await getHealthStatus() } catch { health.value = null } })
</script>

<template>
  <div class="flex min-h-screen bg-slate-50 font-sans text-slate-900">
    <aside class="w-60 bg-slate-900 text-white p-5 flex-col shrink-0 hidden md:flex">
      <div class="flex items-center gap-3 mb-8">
        <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center text-lg font-extrabold">P</div>
        <div>
          <h2 class="font-bold text-sm tracking-tight">PrognoSense</h2>
          <span class="text-[10px] text-slate-400 tracking-wider block">PREDICTIVE MAINTENANCE</span>
        </div>
      </div>
      <nav class="space-y-1">
        <a v-for="m in MENU" :key="m.href" :href="m.href"
           class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-colors"
           :class="aktif(m.href) ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'">
          <span class="text-base w-4 text-center">{{ m.ikon }}</span> {{ m.label }}
        </a>
      </nav>
      <p class="mt-auto text-[11px] text-slate-500 leading-relaxed">
        NASA C-MAPSS FD002 + FD004 · K-Means, LightGBM, Q-Learning
      </p>
    </aside>

    <main class="flex-1 min-w-0">
      <header class="bg-white border-b border-slate-200 px-4 md:px-8 py-4 flex items-center justify-between gap-4">
        <div>
          <div class="text-xs text-slate-500">PrognoSense / <span class="text-cyan-700 font-semibold">{{ halaman.judul }}</span></div>
          <nav class="flex gap-3 mt-1 md:hidden text-xs">
            <a v-for="m in MENU" :key="m.href" :href="m.href" :class="aktif(m.href) ? 'text-cyan-700 font-semibold' : 'text-slate-500'">{{ m.label }}</a>
          </nav>
        </div>
        <Badge :variant="health ? 'default' : 'destructive'" class="px-3 py-1.5 flex items-center gap-2 text-xs whitespace-nowrap">
          <span class="w-2 h-2 rounded-full" :class="health ? 'bg-emerald-400' : 'bg-red-400'"></span>
          {{ health ? `Model ${health.model_version} aktif` : 'Backend offline' }}
        </Badge>
      </header>
      <div class="max-w-7xl mx-auto p-4 md:p-8">
        <component :is="halaman.komp" v-bind="halaman.props" :key="hash" :health="health" />
      </div>
    </main>
  </div>
</template>
