import React, { useEffect, useState } from 'react';
import { Activity, ChevronDown, ChevronRight, Download, FileText } from 'lucide-react';
import api from '../api';

function ConstituencyNode({ node }) {
    if (!node) {
        return null;
    }

    if (node.is_leaf) {
        return (
            <div className="constituency-leaf">
                <span className="constituency-leaf-tag">{node.label}</span>
                <span className="constituency-leaf-word">{node.text}</span>
            </div>
        );
    }

    return (
        <div className="constituency-node">
            <div className="constituency-node-label">{node.label}</div>
            <div className="constituency-node-children">
                {(node.children || []).map((child, index) => (
                    <ConstituencyNode
                        key={`${node.label}-${child.text || child.label}-${index}`}
                        node={child}
                    />
                ))}
            </div>
        </div>
    );
}

function SyntaxPanel({ title, children }) {
    return (
        <div className="syntax-panel">
            <div className="syntax-panel-title">{title}</div>
            {children}
        </div>
    );
}

export default function SyntaxView() {
    const [texts, setTexts] = useState([]);
    const [selectedTextId, setSelectedTextId] = useState(null);
    const [customText, setCustomText] = useState('');
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [expandedSentences, setExpandedSentences] = useState({});

    useEffect(() => {
        const fetchTexts = async () => {
            try {
                const { data } = await api.get('/api/texts');
                setTexts(data);
                if (data.length > 0) {
                    setSelectedTextId(data[0].id);
                }
            } catch (err) {
                console.error('Failed to fetch texts:', err);
            }
        };

        fetchTexts();
    }, []);

    const resetAnalysisState = (data) => {
        setAnalysisResult(data);
        setExpandedSentences({});
    };

    const handleAnalyzeText = async () => {
        if (!selectedTextId) {
            return;
        }

        setIsLoading(true);
        try {
            const { data } = await api.get(`/api/syntax/text/${selectedTextId}`);
            resetAnalysisState(data);
        } catch (err) {
            console.error('Failed to analyze text:', err);
            alert('Failed to analyze text. Make sure the spaCy English model is installed.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleAnalyzeCustomText = async (event) => {
        event.preventDefault();
        if (!customText.trim()) {
            return;
        }

        setIsLoading(true);
        try {
            const { data } = await api.post('/api/syntax/analyze', null, {
                params: { text: customText },
            });
            resetAnalysisState(data);
        } catch (err) {
            console.error('Failed to analyze custom text:', err);
            alert('Failed to analyze text. Make sure the spaCy English model is installed.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleExport = () => {
        if (!analysisResult) {
            return;
        }

        const jsonStr = JSON.stringify(analysisResult.sentences, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');

        link.href = url;
        link.download = 'syntax_analysis.json';
        link.click();
        URL.revokeObjectURL(url);
    };

    const toggleSentence = (index) => {
        setExpandedSentences((prev) => ({
            ...prev,
            [index]: !prev[index],
        }));
    };

    return (
        <div>
            <div className="card">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                    <Activity className="title-icon" size={24} /> Syntax Analysis
                </h2>
                <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
                    Build two syntactic views for every sentence: a constituent system and a dependency tree.
                </p>

                <div style={{ marginBottom: '2rem' }}>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>
                        <FileText size={18} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
                        Analyze Text from Corpus
                    </h3>

                    {texts.length === 0 ? (
                        <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                            Corpus is empty. Add texts in the Corpus tab or use custom text below.
                        </p>
                    ) : (
                        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
                            <select
                                value={selectedTextId || ''}
                                onChange={(event) => setSelectedTextId(Number(event.target.value))}
                                style={{ flex: 1, marginBottom: 0, minWidth: '280px' }}
                            >
                                {texts.map((text) => (
                                    <option key={text.id} value={text.id}>
                                        {text.id} - {text.title} ({text.word_count} words)
                                    </option>
                                ))}
                            </select>
                            <button onClick={handleAnalyzeText} disabled={isLoading || !selectedTextId}>
                                <Activity size={16} className={isLoading ? 'animate-pulse' : ''} />
                                {isLoading ? 'Analyzing...' : 'Analyze'}
                            </button>
                        </div>
                    )}
                </div>

                <div>
                    <h3 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>
                        <FileText size={18} style={{ display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
                        Or Analyze Custom Text
                    </h3>
                    <form onSubmit={handleAnalyzeCustomText}>
                        <textarea
                            rows={6}
                            placeholder="Enter English text to analyze..."
                            value={customText}
                            onChange={(event) => setCustomText(event.target.value)}
                            style={{ marginBottom: '1rem' }}
                        />
                        <button type="submit" disabled={isLoading || !customText.trim()}>
                            <Activity size={16} className={isLoading ? 'animate-pulse' : ''} />
                            {isLoading ? 'Analyzing...' : 'Analyze Custom Text'}
                        </button>
                    </form>
                </div>
            </div>

            {analysisResult && (
                <div className="card animate-fade-in" style={{ marginTop: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                        <h3 style={{ margin: 0 }}>
                            Analysis Results: {analysisResult.total_sentences} sentence(s)
                        </h3>
                        <button onClick={handleExport} className="secondary">
                            <Download size={16} /> Export JSON
                        </button>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {analysisResult.sentences.map((sentence, index) => (
                            <div
                                key={index}
                                style={{
                                    border: '1px solid #2d2d3f',
                                    borderRadius: '8px',
                                    overflow: 'hidden',
                                }}
                            >
                                <button
                                    onClick={() => toggleSentence(index)}
                                    style={{
                                        width: '100%',
                                        padding: '1rem',
                                        backgroundColor: 'var(--surface-hover)',
                                        border: 'none',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px',
                                        cursor: 'pointer',
                                        textAlign: 'left',
                                        color: '#fff',
                                        fontSize: '0.95rem',
                                    }}
                                >
                                    {expandedSentences[index] ? (
                                        <ChevronDown size={18} className="title-icon" />
                                    ) : (
                                        <ChevronRight size={18} className="title-icon" />
                                    )}
                                    <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        Sentence {index + 1}: {sentence.text.substring(0, 100)}
                                        {sentence.text.length > 100 ? '...' : ''}
                                    </span>
                                    <span
                                        style={{
                                            fontSize: '0.8rem',
                                            color: 'var(--text-muted)',
                                            backgroundColor: '#2d2d3f',
                                            padding: '4px 8px',
                                            borderRadius: '4px',
                                        }}
                                    >
                                        {sentence.tokens.length} tokens
                                    </span>
                                </button>

                                {expandedSentences[index] && (
                                    <div style={{ padding: '1.5rem', backgroundColor: '#1a1a24' }}>
                                        <div className="syntax-visual-grid">
                                            <SyntaxPanel title="Constituent System">
                                                <div className="constituency-tree-scroll">
                                                    <ConstituencyNode node={sentence.constituency_tree} />
                                                </div>
                                            </SyntaxPanel>

                                            <SyntaxPanel title="Dependency Tree">
                                                <div
                                                    className="dependency-tree-panel"
                                                    dangerouslySetInnerHTML={{
                                                        __html: sentence.dependency_html || sentence.html || '',
                                                    }}
                                                />
                                            </SyntaxPanel>
                                        </div>

                                        <div style={{ overflowX: 'auto', marginTop: '1.5rem' }}>
                                            <table>
                                                <thead>
                                                    <tr>
                                                        <th>#</th>
                                                        <th>Token</th>
                                                        <th>Lemma</th>
                                                        <th>POS</th>
                                                        <th>Tag</th>
                                                        <th>Dep</th>
                                                        <th>Head</th>
                                                        <th>Head Idx</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {sentence.tokens.map((token, tokenIdx) => (
                                                        <tr key={tokenIdx}>
                                                            <td style={{ color: 'var(--text-muted)' }}>{tokenIdx}</td>
                                                            <td>
                                                                <strong style={{ color: 'var(--primary)' }}>{token.text}</strong>
                                                            </td>
                                                            <td>{token.lemma}</td>
                                                            <td>
                                                                <span
                                                                    style={{
                                                                        backgroundColor: '#8a2be2',
                                                                        color: '#fff',
                                                                        padding: '2px 8px',
                                                                        borderRadius: '4px',
                                                                        fontSize: '0.85rem',
                                                                    }}
                                                                >
                                                                    {token.pos}
                                                                </span>
                                                            </td>
                                                            <td style={{ color: 'var(--text-muted)' }}>{token.tag}</td>
                                                            <td>
                                                                <span
                                                                    style={{
                                                                        backgroundColor: '#00e676',
                                                                        color: '#000',
                                                                        padding: '2px 8px',
                                                                        borderRadius: '4px',
                                                                        fontSize: '0.85rem',
                                                                    }}
                                                                >
                                                                    {token.dep}
                                                                </span>
                                                            </td>
                                                            <td>{token.head}</td>
                                                            <td style={{ color: 'var(--text-muted)' }}>{token.head_idx}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
