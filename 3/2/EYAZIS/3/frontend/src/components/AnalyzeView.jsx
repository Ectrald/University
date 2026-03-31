import React, { useState } from 'react';
import { Activity, FlaskConical } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api';

export default function AnalyzeView() {
    const [text, setText] = useState('');
    const [result, setResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!text.trim()) return;

        setIsLoading(true);
        try {
            const { data } = await api.post('/api/analyze', { text });
            setResult(data);
        } catch (err) {
            console.error(err);
            alert('Failed to analyze text');
        } finally {
            setIsLoading(false);
        }
    };

    const posData = result?.pos_distribution
        ? Object.entries(result.pos_distribution).map(([name, count]) => ({ name, count }))
        : [];

    const freqData = result?.word_frequency
        ? Object.entries(result.word_frequency).slice(0, 20).map(([name, count]) => ({ name, count }))
        : [];

    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <Activity className="title-icon" size={24} /> Text Analysis
            </h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                Analyze text "on the fly" without saving it to the database.
            </p>

            <form onSubmit={handleAnalyze} style={{ marginBottom: '2.5rem' }}>
                <textarea
                    rows={8}
                    placeholder="Enter text to analyze here..."
                    value={text}
                    onChange={e => setText(e.target.value)}
                    required
                />
                <button type="submit" disabled={isLoading}>
                    <FlaskConical size={16} className={isLoading ? 'animate-pulse' : ''} />
                    {isLoading ? 'Analyzing...' : 'Analyze Text'}
                </button>
            </form>

            {result && (
                <div className="animate-fade-in">
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '2.5rem' }}>
                        <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Total Words</div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{result.total_words}</div>
                        </div>
                        <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Unique Words</div>
                            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{result.unique_words}</div>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
                        {posData.length > 0 && (
                            <div>
                                <h3 style={{ marginBottom: '1rem' }}>POS Distribution</h3>
                                <div style={{ height: '250px' }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={posData}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3f" />
                                            <XAxis dataKey="name" stroke="#9fa6b2" fontSize={12} />
                                            <YAxis stroke="#9fa6b2" fontSize={12} />
                                            <Tooltip contentStyle={{ backgroundColor: '#1a1a24', border: '1px solid #2d2d3f' }} />
                                            <Bar dataKey="count" fill="#8a2be2" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        )}

                        {freqData.length > 0 && (
                            <div>
                                <h3 style={{ marginBottom: '1rem' }}>Top 20 Frequencies</h3>
                                <div style={{ height: '250px' }}>
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={freqData} layout="vertical">
                                            <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3f" />
                                            <XAxis type="number" stroke="#9fa6b2" fontSize={12} />
                                            <YAxis dataKey="name" type="category" stroke="#9fa6b2" fontSize={12} width={80} />
                                            <Tooltip contentStyle={{ backgroundColor: '#1a1a24', border: '1px solid #2d2d3f' }} />
                                            <Bar dataKey="count" fill="#00e676" radius={[0, 4, 4, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
