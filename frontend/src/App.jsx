import React, { useState } from 'react';
import { UploadCloud, FileText, Sparkles, Loader2, LogOut } from 'lucide-react';
import AccessGate from './components/AccessGate';
import ResultsSection from './components/ResultsSection';
import { analyzeResume } from './lib/api';

function App() {
  const [hasAccess, setHasAccess] = useState(false);
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  if (!hasAccess) {
    return <AccessGate onAccessGranted={() => setHasAccess(true)} />;
  }

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
      if (err.message === "Invalid or missing Access Code") {
        localStorage.removeItem('app_access_code');
        setHasAccess(false);
        return;
      }
      setError(err.message || 'Something went wrong. Please check your API key/Access Code.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.svg" alt="Logo" className="w-10 h-10" />
            <h1 className="text-xl font-bold text-gray-900">AI Resume Builder</h1>
          </div>
          <button
            onClick={() => {
              localStorage.removeItem('app_access_code');
              setHasAccess(false);
            }}
            className="text-sm text-gray-500 hover:text-gray-900 flex items-center gap-2"
          >
            <LogOut className="w-4 h-4" />
            Change Code
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-extrabold text-gray-900 mb-4">
            Tailor Your Resume in Seconds
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Upload your resume and a job description to get instant feedback, skill gap analysis, and a tailored cover letter.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden mb-10">
          <form onSubmit={handleSubmit} className="p-8 grid md:grid-cols-2 gap-8">
            {/* Resume Upload */}
            <div className="space-y-4">
              <label className="block text-sm font-semibold text-gray-700">
                1. Upload Resume (PDF/TXT)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors bg-gray-50">
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
                      <FileText className="w-12 h-12 text-blue-600 mb-3" />
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

            {/* JD Input */}
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

            {/* Submit Action */}
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
                  flex items-center gap-2 px-8 py-3 rounded-full font-bold text-white shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5
                  ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'}
                `}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate Analysis
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Results Area */}
        {results && <ResultsSection results={results} />}
      </main>
    </div>
  );
}

export default App;
