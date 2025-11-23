const API_BASE = import.meta.env.DEV ? 'http://localhost:8000/api' : '/api';

export const getAccessCode = () => localStorage.getItem('app_access_code');
export const setAccessCode = (code) => localStorage.setItem('app_access_code', code);

const headers = () => ({
  'x-access-code': getAccessCode() || '',
});

export async function analyzeResume(formData) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: headers(),
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Analysis failed');
  }
  return response.json();
}

export async function rewriteBullets(bullets, jdText) {
  const response = await fetch(`${API_BASE}/rewrite`, {
    method: 'POST',
    headers: {
      ...headers(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ bullets, jd_text: jdText }),
  });
  if (!response.ok) throw new Error('Cover letter generation failed');
  return response.json();
}
