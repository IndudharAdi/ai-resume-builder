import React, { useState, useEffect } from 'react';
import { Lock } from 'lucide-react';
import { setAccessCode, getAccessCode } from '../lib/api';

export default function AccessGate({ onAccessGranted }) {
    const [code, setCode] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        const saved = getAccessCode();
        if (saved) {
            // Optimistically grant access, API will reject if invalid
            onAccessGranted();
        }
    }, [onAccessGranted]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!code.trim()) {
            setError('Please enter a code');
            return;
        }
        setAccessCode(code.trim());
        onAccessGranted();
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
                <div className="flex flex-col items-center mb-6">
                    <div className="bg-blue-100 p-3 rounded-full mb-4">
                        <Lock className="w-8 h-8 text-blue-600" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Restricted Access</h2>
                    <p className="text-gray-500 text-center mt-2">
                        This is a private tool. Please enter the access code to continue.
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <input
                            type="password"
                            value={code}
                            onChange={(e) => setCode(e.target.value)}
                            placeholder="Enter Access Code"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
                        />
                        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-600 text-white py-2 rounded-lg font-semibold hover:bg-blue-700 transition duration-200"
                    >
                        Enter
                    </button>
                </form>
            </div>
        </div>
    );
}
