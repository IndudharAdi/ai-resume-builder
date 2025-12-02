import React from 'react';
import ReactMarkdown from 'react-markdown';
import { CheckCircle, XCircle, Copy, Download, Target, TrendingUp } from 'lucide-react';
import { downloadDocx } from '../lib/api';

export default function ResultsSection({ results }) {
    if (!results) return null;

    const { jd_skills, resume_skills, missing_skills, overlap_skills, rewritten_bullets, cover_letter, tailored_resume, ats_score, ats_breakdown, ats_recommendations } = results;

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Copied to clipboard!');
    };

    const downloadCoverLetter = () => {
        const element = document.createElement("a");
        const file = new Blob([cover_letter], { type: 'text/plain' });
        element.href = URL.createObjectURL(file);
        element.download = "cover_letter.txt";
        document.body.appendChild(element);
        element.click();
    };

    return (
        <div className="space-y-8 animate-fadeIn">
            {/* ATS Compatibility Score */}
            {ats_score !== undefined && (
                <div className="glass-effect rounded-2xl p-8 shadow-xl border-2 border-blue-200 animate-scaleIn">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <Target className="w-8 h-8 text-blue-600" />
                            <h3 className="text-2xl font-bold text-gray-900">ATS Compatibility Score</h3>
                        </div>
                        <div className="text-right">
                            <div className={`text-5xl font-extrabold ${ats_score >= 80 ? 'text-green-600' :
                                ats_score >= 60 ? 'text-yellow-600' :
                                    'text-red-600'
                                }`}>
                                {ats_score}
                                <span className="text-2xl text-gray-500">/100</span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                                {ats_score >= 80 ? 'Excellent Match' :
                                    ats_score >= 60 ? 'Good Match' :
                                        'Needs Improvement'}
                            </p>
                        </div>
                    </div>

                    {/* Score Breakdown */}
                    {ats_breakdown && (
                        <div className="grid md:grid-cols-2 gap-4 mb-6">
                            {Object.entries(ats_breakdown).map(([key, value]) => {
                                const maxScores = { keywords: 40, format: 20, sections: 20, contact: 10, length: 10 };
                                const maxScore = maxScores[key] || 100;
                                const percentage = (value / maxScore) * 100;
                                return (
                                    <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-semibold text-gray-700 capitalize">{key}</span>
                                            <span className="text-sm font-bold text-gray-900">{value}/{maxScore}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                                            <div
                                                className={`h-2.5 rounded-full ${percentage >= 80 ? 'bg-green-500' :
                                                    percentage >= 60 ? 'bg-yellow-500' :
                                                        'bg-red-500'
                                                    }`}
                                                style={{ width: `${percentage}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {/* Recommendations */}
                    {ats_recommendations && ats_recommendations.length > 0 && (
                        <div className="bg-white rounded-lg p-6 shadow-sm">
                            <div className="flex items-center gap-2 mb-4">
                                <TrendingUp className="w-5 h-5 text-blue-600" />
                                <h4 className="text-lg font-bold text-gray-900">Recommendations</h4>
                            </div>
                            <ul className="space-y-3">
                                {ats_recommendations.map((rec, idx) => (
                                    <li key={idx} className="flex gap-3 text-gray-700">
                                        <span className="text-blue-500 font-bold mt-1">•</span>
                                        <span>{rec}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* Skills Analysis */}
            <div className="grid md:grid-cols-2 gap-6">
                <div className="glass-effect border-2 border-green-300 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
                    <div className="flex items-center gap-2 mb-4">
                        <CheckCircle className="text-green-600" />
                        <h3 className="text-lg font-semibold text-green-900">Matching Skills</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {overlap_skills.map(skill => (
                            <span key={skill} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                                {skill}
                            </span>
                        ))}
                        {overlap_skills.length === 0 && <span className="text-gray-500 italic">No direct matches found.</span>}
                    </div>
                </div>

                <div className="glass-effect border-2 border-red-300 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
                    <div className="flex items-center gap-2 mb-4">
                        <XCircle className="text-red-600" />
                        <h3 className="text-lg font-semibold text-red-900">Missing Skills</h3>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {missing_skills.map(skill => (
                            <span key={skill} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                                {skill}
                            </span>
                        ))}
                        {missing_skills.length === 0 && <span className="text-gray-500 italic">Great job! No missing skills detected.</span>}
                    </div>
                </div>
            </div>

            {/* Rewritten Bullets */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900">Rewritten Bullet Points</h3>
                    <button
                        onClick={() => copyToClipboard(JSON.stringify(rewritten_bullets, null, 2))}
                        className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                    >
                        <Copy size={16} /> Copy JSON
                    </button>
                </div>
                <ul className="space-y-3">
                    {rewritten_bullets.map((bullet, idx) => (
                        <li key={idx} className="flex gap-3 text-gray-700">
                            <span className="text-blue-500 font-bold">•</span>
                            <span>{bullet}</span>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Cover Letter */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900">Generated Cover Letter</h3>
                    <div className="flex gap-3">
                        <button
                            onClick={() => copyToClipboard(cover_letter)}
                            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
                        >
                            <Copy size={16} /> Copy
                        </button>
                        <button
                            onClick={downloadCoverLetter}
                            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                        >
                            <Download size={16} /> Download
                        </button>
                    </div>
                </div>
                <div className="prose max-w-none text-gray-700 bg-gray-50 p-6 rounded-lg border border-gray-100">
                    <ReactMarkdown>{cover_letter}</ReactMarkdown>
                </div>
            </div>

            {/* Tailored Resume */}
            {tailored_resume && (
                <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-bold text-gray-900">Tailored Resume</h3>
                        <div className="flex gap-3">
                            <button
                                onClick={() => copyToClipboard(tailored_resume)}
                                className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
                            >
                                <Copy size={16} /> Copy
                            </button>
                            <button
                                onClick={() => {
                                    const element = document.createElement("a");
                                    const file = new Blob([tailored_resume], { type: 'text/plain' });
                                    element.href = URL.createObjectURL(file);
                                    element.download = "tailored_resume.txt";
                                    document.body.appendChild(element);
                                    element.click();
                                }}
                                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                            >
                                <Download size={16} /> TXT
                            </button>
                            <button
                                onClick={async () => {
                                    try {
                                        const blob = await downloadDocx(results.tailored_resume);
                                        const url = window.URL.createObjectURL(blob);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = "tailored_resume.docx";
                                        document.body.appendChild(a);
                                        a.click();
                                        a.remove();
                                    } catch (err) {
                                        alert("Failed to download DOCX: " + err.message);
                                    }
                                }}
                                className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                            >
                                <Download size={16} /> Word
                            </button>
                        </div>
                    </div>
                    <div className="prose max-w-none text-gray-700 bg-gray-50 p-6 rounded-lg border border-gray-100">
                        <ReactMarkdown>{tailored_resume}</ReactMarkdown>
                    </div>
                </div>
            )}
        </div>
    );
}
