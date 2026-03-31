import React, { useState, useEffect } from 'react';
import { BarChart2, RefreshCw } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import api from '../api';

export default function StatisticsView() {
    const [stats, setStats] = useState(null);
    const [freq, setFreq] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const fetchStats = async () => {
        setIsLoading(true);
        try {
            const [statsRes, freqRes] = await Promise.all([
                api.get('/api/statistics'),
                api.get('/api/frequency', { params: { top_n: 30 } })
            ]);
            setStats(statsRes.data);
            setFreq(freqRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const posData = stats?.pos_distribution
        ? Object.entries(stats.pos_distribution).map(([name, count]) => ({ name, count }))
        : [];

    return (
        <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                    <BarChart2 className="title-icon" size={24} /> Corpus Statistics
                </h2>
                <button onClick={fetchStats} disabled={isLoading} className="secondary">
                    <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} /> Refresh
                </button>
            </div>

            {stats && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                    <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Total Words</div>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{stats.total_words}</div>
                    </div>
                    <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Unique Words</div>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{stats.unique_words}</div>
                    </div>
                    <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', textAlign: 'center' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Total Texts</div>
                        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>{stats.total_texts}</div>
                    </div>
                </div>
            )}

            {posData.length > 0 && (
                <div style={{ marginBottom: '2.5rem' }}>
                    <h3>POS Distribution</h3>
                    <div style={{ height: '300px', marginTop: '1rem' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={posData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#2d2d3f" />
                                <XAxis dataKey="name" stroke="#9fa6b2" />
                                <YAxis stroke="#9fa6b2" />
                                <Tooltip contentStyle={{ backgroundColor: '#1a1a24', border: '1px solid #2d2d3f' }} />
                                <Bar dataKey="count" fill="#8a2be2" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}

            {freq?.top_words && freq.top_words.length > 0 && (
                <div>
                    <h3>Top Words</h3>
                    <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>Word</th>
                                    <th>Frequency</th>
                                </tr>
                            </thead>
                            <tbody>
                                {freq.top_words.map((w, i) => (
                                    <tr key={i}>
                                        <td><strong style={{ color: 'var(--text)' }}>{w.word}</strong></td>
                                        <td style={{ color: 'var(--primary)' }}>{w.frequency}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
