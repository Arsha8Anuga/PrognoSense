// Semua panggilan API di satu tempat. Alamat relatif: lewat nginx di server, lewat proxy Vite saat dev.
async function baca(res) {
  const teks = await res.text()
  let isi
  try { isi = JSON.parse(teks) } catch { isi = { error: { pesan: teks } } }
  if (!res.ok) {
    const e = new Error(isi?.error?.pesan || isi?.detail || `HTTP ${res.status}`)
    e.detail = isi?.error?.detail || []
    throw e
  }
  return isi
}

export const getJSON = (path) => fetch(path).then(baca)

export function uploadCSV(file, rasio = 100, sampaiRusak = false) {
  const form = new FormData()
  form.append('file', file)
  form.append('rasio', String(rasio))
  form.append('sampai_rusak', String(sampaiRusak))
  return fetch('/api/prediksi', { method: 'POST', body: form }).then(baca)
}

export const getHealthStatus = () => getJSON('/health')
