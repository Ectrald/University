import React, { useState } from 'react';
import { FileText, Search } from 'lucide-react';
import api from '../api';

export default function ConcordanceView() {
    const [lemma, setLemma] = useState('');
    const [winSize, setWinSize] = useState(5);
    const [kwic, setKwic] = useState([]);
    const [collocates, setCollocates] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!lemma.trim()) return;

        setIsLoading(true);
        setHasSearched(true);
        try {
            const [kwicRes, collRes] = await Promise.all([
                api.get('/api/concordance/kwic', { params: { lemma, window: winSize } }),
                api.get('/api/concordance/collocates', { params: { lemma, window: winSize } })
            ]);
            setKwic(Array.isArray(kwicRes.data) ? kwicRes.data : []);
            const collData = collRes.data;
            setCollocates(collData && typeof collData === 'object' && !Array.isArray(collData) ? collData : {});
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    const collocatesList = Object.entries(collocates)
        .map(([word, frequency]) => ({ word, frequency }))
        .sort((a, b) => b.frequency - a.frequency);

    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <FileText className="title-icon" size={24} /> Concordance Search
            </h2>

            <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
                <input
                    style={{ flex: 3, margin: 0 }}
                    placeholder="Enter lemma..."
                    value={lemma}
                    onChange={e => setLemma(e.target.value)}
                    required
                />
                <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <label style={{ color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>Window:</label>
                    <input
                        type="number"
                        min="1"
                        max="20"
                        value={winSize}
                        onChange={e => setWinSize(parseInt(e.target.value) || 5)}
                        style={{ margin: 0 }}
                    />
                </div>
                <button type="submit" disabled={isLoading}>
                    <Search size={16} className={isLoading ? 'animate-spin' : ''} /> Search
                </button>
            </form>

            {hasSearched && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem' }}>
                    {/* KWIC Results */}
                    <div>
                        <h3 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>
                            KWIC Results {kwic.length > 0 && <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', fontSize: '0.9rem' }}>({kwic.length} found)</span>}
                        </h3>
                        {kwic.length === 0 ? (
                            <p style={{ color: 'var(--text-muted)' }}>No KWIC results found.</p>
                        ) : (
                            <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Text</th>
                                            <th style={{ textAlign: 'right' }}>Left Context</th>
                                            <th style={{ textAlign: 'center' }}>Keyword</th>
                                            <th>Right Context</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {kwic.map((k, i) => (
                                            <tr key={i}>
                                                <td style={{ whiteSpace: 'nowrap', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                                    {k.text_title}
                                                </td>
                                                <td style={{ textAlign: 'right', color: 'var(--text)' }}>
                                                    {k.left}
                                                </td>
                                                <td style={{ textAlign: 'center' }}>
                                                    <strong style={{
                                                        color: 'var(--primary)',
                                                        backgroundColor: 'rgba(138,43,226,0.15)',
                                                        padding: '2px 8px',
                                                        borderRadius: '4px',
                                                        whiteSpace: 'nowrap'
                                                    }}>
                                                        {k.keyword}
                                                    </strong>
                                                </td>
                                                <td style={{ color: 'var(--text)' }}>
                                                    {k.right}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>

                    {/* Collocates */}
                    <div>
                        <h3 style={{ marginBottom: '1rem', color: 'var(--primary)' }}>
                            Collocates {collocatesList.length > 0 && <span style={{ color: 'var(--text-muted)', fontWeight: 'normal', fontSize: '0.9rem' }}>({collocatesList.length})</span>}
                        </h3>
                        {collocatesList.length === 0 ? (
                            <p style={{ color: 'var(--text-muted)' }}>No collocates found.</p>
                        ) : (
                            <div style={{ overflowX: 'auto', maxHeight: '300px', overflowY: 'auto' }}>
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Collocate</th>
                                            <th>Frequency</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {collocatesList.map((c, i) => (
                                            <tr key={i}>
                                                <td><strong>{c.word}</strong></td>
                                                <td style={{ color: 'var(--primary)' }}>{c.frequency}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
