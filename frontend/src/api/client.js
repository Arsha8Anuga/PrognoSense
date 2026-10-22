const BASE_URL = '/api';

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/prediksi`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Gagal melakukan prediksi');
  }

  return await response.json();
}

export async function getHealthStatus() {
  const response = await fetch('/health');
  return await response.json();
}