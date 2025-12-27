import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { UploadCloud, FileText, Loader2, LogOut } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import ResultsSection from './components/ResultsSection';
import { analyzeResume } from './lib/api';

function Dashboard() {
  const { logout, user } = useAuth();
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !jdText.trim()) {
      setError('Please provide both a resume and a job description.');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const formData = new FormData();
      formData.append('resume_file', file);
      formData.append('jd_text', jdText);

      const data = await analyzeResume(formData);
      setResults(data);
    } catch (err) {
      if (err.message === "Could not validate credentials") {
        logout();
        return;
      }
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen pb-0">
      <header className="glass-effect sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-700 to-blue-500 bg-clip-text text-transparent">
            ResumeBoost
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500 hidden md:block">{user?.email}</span>
            <button
              onClick={logout}
              className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2 transition-all hover:scale-105"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="text-center mb-12 animate-fadeIn">
          <h2 className="text-5xl font-extrabold bg-gradient-to-r from-blue-700 via-blue-600 to-cyan-500 bg-clip-text text-transparent mb-4">
            Boost Your Resume, Land Your Dream Job
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your resume and a job description to get instant feedback, skill gap analysis, and a tailored cover letter.
          </p>
        </div>

        <div className="glass-effect rounded-2xl shadow-xl overflow-hidden mb-10 animate-slideUp">
          <form onSubmit={handleSubmit} className="p-8 grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <label className="block text-sm font-semibold text-gray-700">
                1. Upload Resume (PDF/TXT)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 hover:bg-blue-50/50 transition-all duration-300 bg-gray-50">
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.txt"
                  className="hidden"
                  id="resume-upload"
                />
                <label htmlFor="resume-upload" className="cursor-pointer flex flex-col items-center">
                  {file ? (
                    <>
                      <FileText className="w-12 h-12 text-blue-600 mb-3 animate-scaleIn" />
                      <span className="font-medium text-gray-900">{file.name}</span>
                      <span className="text-sm text-gray-500 mt-1">Click to change</span>
                    </>
                  ) : (
                    <>
                      <UploadCloud className="w-12 h-12 text-gray-400 mb-3" />
                      <span className="font-medium text-gray-600">Click to upload or drag & drop</span>
                      <span className="text-sm text-gray-400 mt-1">PDF or TXT files only</span>
                    </>
                  )}
                </label>
              </div>
            </div>

            <div className="space-y-4">
              <label className="block text-sm font-semibold text-gray-700">
                2. Job Description
              </label>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste the job description here..."
                className="w-full h-48 p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none bg-gray-50"
              />
            </div>

            <div className="md:col-span-2 flex flex-col items-center pt-4">
              {error && (
                <div className="bg-red-50 text-red-600 px-4 py-2 rounded-lg mb-4 text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className={`
                  flex items-center gap-2 px-8 py-3 rounded-full font-bold text-white shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-1 hover:scale-105
                  ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:from-blue-700 hover:via-blue-600 hover:to-cyan-600'}
                `}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  'Get My Analysis'
                )}
              </button>
            </div>
          </form>
        </div>

        {results && <ResultsSection results={results} />}
      </main>

      <footer className="border-t border-gray-200 py-6 mt-20">
        <div className="max-w-5xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-600">
            © {new Date().getFullYear()} ResumeBoost. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-10 h-10 animate-spin text-blue-600" /></div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-10 h-10 animate-spin text-blue-600" /></div>;
  }

  if (user) {
    return <Navigate to="/" />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
