import React, { useState, useEffect } from 'react';
import { Search, Loader } from 'lucide-react';
import api from '../api';

export default function SearchView() {
    const [query, setQuery] = useState('');
    const [posFilter, setPosFilter] = useState('ALL');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const fetchResults = async () => {
            if (query.trim() === '') {
                setResults([]);
                return;
            }
            setIsLoading(true);
            try {
                const { data } = await api.get('/api/search', { params: { query } });
                setResults(data);
            } catch (err) {
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        const debounce = setTimeout(fetchResults, 150);
        return () => clearTimeout(debounce);
    }, [query]);

    const filteredResults = results.filter(r => {
        if (posFilter === 'ALL') return true;
        return r.pos === posFilter;
    });

    const uniquePos = ['ALL', ...new Set(results.map(r => r.pos).filter(Boolean))].sort();

    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <Search className="title-icon" size={24} /> Real-time Search
            </h2>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
                <input
                    autoFocus
                    type="text"
                    placeholder="Start typing a word or lemma..."
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    style={{ flex: 1, margin: 0, fontSize: '1.1rem', padding: '1rem' }}
                />

                {results.length > 0 && (
                    <select
                        value={posFilter}
                        onChange={e => setPosFilter(e.target.value)}
                        style={{ width: '200px', margin: 0 }}
                    >
                        {uniquePos.map(pos => (
                            <option key={pos} value={pos}>{pos === 'ALL' ? 'All Parts of Speech' : pos}</option>
                        ))}
                    </select>
                )}
            </div>

            <div style={{ position: 'relative', minHeight: '200px' }}>
                {isLoading && query && (
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', justifyContent: 'center', paddingTop: '2rem', backgroundColor: 'rgba(26,26,36,0.7)', zIndex: 10 }}>
                        <div className="animate-spin" style={{ animation: 'spin 1s linear infinite' }}>
                            <Loader size={32} color="var(--primary)" />
                        </div>
                        <style>
                            {`@keyframes spin { 100% { transform: rotate(360deg); } }`}
                        </style>
                    </div>
                )}

                {!isLoading && query && filteredResults.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No results found for "{query}".
                    </div>
                )}

                {!query && (
                    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        Type in the search box to find words and their variations across the corpus instantly.
                    </div>
                )}

                {filteredResults.length > 0 && (
                    <div className="animate-fade-in" style={{ overflowX: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Word</th>
                                    <th>Lemma</th>
                                    <th>POS</th>
                                    <th>Freq</th>
                                    <th>Morph Tags</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredResults.map(r => (
                                    <tr key={r.id}>
                                        <td>{r.id}</td>
                                        <td><strong style={{ color: 'var(--text)' }}>{r.word}</strong></td>
                                        <td style={{ color: 'var(--primary)' }}>{r.lemma}</td>
                                        <td><span style={{
                                            backgroundColor: 'rgba(138,43,226,0.2)',
                                            padding: '2px 8px',
                                            borderRadius: '12px',
                                            fontSize: '0.8rem',
                                            fontWeight: 'bold',
                                            color: 'var(--primary)'
                                        }}>{r.pos}</span></td>
                                        <td>{r.frequency}</td>
                                        <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{r.morph_tags}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
