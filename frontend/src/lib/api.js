const API_BASE = import.meta.env.DEV ? 'http://127.0.0.1:8000/api' : '/api';

const getAuthHeader = () => {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export async function analyzeResume(formData) {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: getAuthHeader(),
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
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ bullets, jd_text: jdText }),
  });
  if (!response.ok) throw new Error('Rewrite failed');
  return response.json();
}

export async function downloadDocx(text) {
  const response = await fetch(`${API_BASE}/download-docx`, {
    method: 'POST',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Download failed');
  }
  return response.blob();
}

export async function generateCoverLetter(resumeText, jdText) {
  const response = await fetch(`${API_BASE}/cover-letter`, {
    method: 'POST',
    headers: {
      ...getAuthHeader(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ resume_text: resumeText, jd_text: jdText }),
  });
  if (!response.ok) throw new Error('Cover letter generation failed');
  return response.json();
}
