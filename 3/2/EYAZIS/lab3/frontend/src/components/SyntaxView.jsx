import React, { useState, useEffect } from 'react';
import { Network, Download, Save, RefreshCw, ChevronDown, ChevronRight, Edit3 } from 'lucide-react';
import api from '../api';

export default function SyntaxView() {
    const [texts, setTexts] = useState([]);
    const [selectedTextId, setSelectedTextId] = useState('');
    const [analyses, setAnalyses] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    
    // Editing state
    const [editingSentenceId, setEditingSentenceId] = useState(null);
    const [editTokens, setEditTokens] = useState([]);
    const [isSavingDetails, setIsSavingDetails] = useState(false);

    useEffect(() => {
        fetchTexts();
    }, []);

    const fetchTexts = async () => {
        try {
            const { data } = await api.get('/api/texts');
            setTexts(data);
        } catch (err) {
            console.error(err);
        }
    };

    const fetchAnalyses = async (textId) => {
        setIsLoading(true);
        try {
            const { data } = await api.get(`/api/syntactic-analysis/${textId}`);
            const parsedData = data.map(item => ({
                ...item,
                tokens: JSON.parse(item.result_json)
            }));
            setAnalyses(parsedData);
            setEditingSentenceId(null);
        } catch (err) {
            console.error(err);
            alert('Failed to fetch analyses');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSelectText = (e) => {
        const id = e.target.value;
        setSelectedTextId(id);
        if (id) fetchAnalyses(id);
        else setAnalyses([]);
    };

    const handleAnalyze = async () => {
        if (!selectedTextId) return;
        setIsLoading(true);
        try {
            await api.post(`/api/syntactic-analysis/analyze-and-save/${selectedTextId}`);
            await fetchAnalyses(selectedTextId);
        } catch (err) {
            console.error(err);
            alert('Failed to analyze text');
            setIsLoading(false);
        }
    };

    const handleExport = () => {
        if (!analyses.length) return;
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(analyses, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", `syntactic_analysis_${selectedTextId}.json`);
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    };

    const startEditing = (analysis) => {
        setEditingSentenceId(analysis.id);
        setEditTokens(JSON.parse(JSON.stringify(analysis.tokens))); // deep copy
    };

    const cancelEditing = () => {
        setEditingSentenceId(null);
        setEditTokens([]);
    };

    const handleTokenChange = (index, field, value) => {
        const newTokens = [...editTokens];
        newTokens[index][field] = value;
        
        // Ensure head_id is integer
        if (field === 'head_id') {
            newTokens[index][field] = parseInt(value, 10);
            const headToken = newTokens.find(t => t.id === newTokens[index].head_id);
            if (headToken) {
                newTokens[index].head_text = headToken.text;
            } else {
                newTokens[index].head_text = '';
            }
        }
        setEditTokens(newTokens);
    };

    const saveDetails = async () => {
        if (!editingSentenceId) return;
        setIsSavingDetails(true);
        try {
            const result_json = JSON.stringify(editTokens);
            await api.put(`/api/syntactic-analysis/update/${editingSentenceId}`, { result_json });
            
            // Update local state
            setAnalyses(prev => prev.map(a => 
                a.id === editingSentenceId 
                    ? { ...a, result_json, tokens: editTokens }
                    : a
            ));
            
            setEditingSentenceId(null);
        } catch (err) {
            console.error(err);
            alert('Failed to save changes');
        } finally {
            setIsSavingDetails(false);
        }
    };

    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <Network className="title-icon" size={24} /> Syntactic Analysis
            </h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                Select a text to view or generate its syntactic dependency tree. You can edit the relations and export them.
            </p>

            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
                <select 
                    value={selectedTextId} 
                    onChange={handleSelectText} 
                    style={{ flex: 1, padding: '0.75rem', borderRadius: '4px', backgroundColor: 'var(--surface-hover)', color: 'var(--text)', border: '1px solid var(--border)' }}
                >
                    <option value="">-- Select a text from Corpus --</option>
                    {texts.map(t => (
                        <option key={t.id} value={t.id}>[{t.id}] {t.title}</option>
                    ))}
                </select>
                <button onClick={fetchTexts} disabled={isLoading} className="secondary" title="Refresh Text List">
                    <RefreshCw size={16} />
                </button>
            </div>

            {selectedTextId && (
                <div>
                    {isLoading ? (
                        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                            <RefreshCw className="animate-spin title-icon" size={32} style={{ marginBottom: '1rem' }} />
                            <p>Processing...</p>
                        </div>
                    ) : analyses.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem', backgroundColor: 'var(--surface-hover)', borderRadius: '8px' }}>
                            <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>No syntactic analysis found for this text.</p>
                            <button onClick={handleAnalyze}>
                                <Network size={16} /> Analyze Document & Save
                            </button>
                        </div>
                    ) : (
                        <div className="animate-fade-in">
                            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
                                <button onClick={handleExport} style={{ backgroundColor: '#2e7d32' }}>
                                    <Download size={16} /> Export JSON
                                </button>
                            </div>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {analyses.map((analysis, index) => {
                                    const isEditing = editingSentenceId === analysis.id;
                                    const displayTokens = isEditing ? editTokens : analysis.tokens;
                                    
                                    return (
                                        <div key={analysis.id} style={{ backgroundColor: 'var(--surface-hover)', borderRadius: '8px', overflow: 'hidden' }}>
                                            <div style={{ padding: '1rem', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                <div>
                                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                                                        Sentence {analysis.sentence_index + 1}
                                                    </div>
                                                    <div style={{ fontWeight: '500' }}>{analysis.original_sentence}</div>
                                                </div>
                                                {!isEditing && (
                                                    <button className="secondary" onClick={() => startEditing(analysis)} style={{ padding: '0.5rem' }}>
                                                        <Edit3 size={16} /> Edit
                                                    </button>
                                                )}
                                            </div>
                                            
                                            <div style={{ padding: '1rem', overflowX: 'auto' }}>
                                                <table style={{ minWidth: '100%', borderCollapse: 'collapse' }}>
                                                    <thead>
                                                        <tr>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>ID</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>Word</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>Lemma</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>POS</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>Dependency</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>Head ID</th>
                                                            <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-muted)' }}>Head Word</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {displayTokens.map((token, tIdx) => (
                                                            <tr key={tIdx} style={{ borderTop: '1px solid var(--border)' }}>
                                                                <td style={{ padding: '8px' }}>{token.id}</td>
                                                                <td style={{ padding: '8px' }}>{token.text}</td>
                                                                <td style={{ padding: '8px' }}>{token.lemma}</td>
                                                                <td style={{ padding: '8px' }}>
                                                                    {isEditing ? (
                                                                        <input 
                                                                            value={token.pos} 
                                                                            onChange={e => handleTokenChange(tIdx, 'pos', e.target.value)} 
                                                                            style={{ padding: '4px', width: '60px' }} 
                                                                        />
                                                                    ) : token.pos}
                                                                </td>
                                                                <td style={{ padding: '8px' }}>
                                                                    {isEditing ? (
                                                                        <input 
                                                                            value={token.dep} 
                                                                            onChange={e => handleTokenChange(tIdx, 'dep', e.target.value)} 
                                                                            style={{ padding: '4px', width: '80px' }} 
                                                                        />
                                                                    ) : token.dep}
                                                                </td>
                                                                <td style={{ padding: '8px' }}>
                                                                    {isEditing ? (
                                                                        <input 
                                                                            type="number"
                                                                            value={token.head_id} 
                                                                            onChange={e => handleTokenChange(tIdx, 'head_id', e.target.value)} 
                                                                            style={{ padding: '4px', width: '60px' }} 
                                                                        />
                                                                    ) : token.head_id}
                                                                </td>
                                                                <td style={{ padding: '8px' }}>{token.head_text}</td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                                
                                                {isEditing && (
                                                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'flex-end' }}>
                                                        <button disabled={isSavingDetails} onClick={saveDetails}>
                                                            <Save size={16} /> Save Changes
                                                        </button>
                                                        <button disabled={isSavingDetails} className="secondary" onClick={cancelEditing}>
                                                            Cancel
                                                        </button>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
