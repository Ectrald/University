import React, { useState } from 'react';
import { Clock } from 'lucide-react';
import api from '../api';

export default function TestingView() {
    const [results, setResults] = useState([]);
    const [isRunning, setIsRunning] = useState(false);

    const runTest = async () => {
        setIsRunning(true);
        setResults([]);

        const logs = [];
        const addLog = (msg) => {
            logs.push(msg);
            setResults([...logs]);
        };

        try {
            const base_text = "The domestic cat is a small, typically furry, carnivorous mammal. They are often called house cats when kept as indoor pets or simply cats when there is no need to distinguish them from other felids and felines. They are often valued by humans for companionship and for their ability to hunt vermin. There are more than seventy cat breeds. Cats are similar in anatomy to the other felid species: they have a strong flexible body, quick reflexes, sharp teeth and retractable claws adapted to killing small prey. Cat senses fit a crepuscular and predatory ecological niche. Cats can hear sounds too faint or too high in frequency for human ears, such as those made by mice and other small animals. They can see in near darkness. ";
            const short_text = base_text;
            const medium_text = base_text.repeat(10);
            const long_text = base_text.repeat(50);

            addLog("### – Performance Test Started");
            addLog("### – NLP Analysis Test");

            let t0 = performance.now();
            let res = await api.post("/api/analyze", { text: short_text });
            let t1 = performance.now();
            addLog(`Short text (${res.data.total_words} words): ${((t1 - t0) / 1000).toFixed(4)} sec`);

            t0 = performance.now();
            res = await api.post("/api/analyze", { text: medium_text });
            t1 = performance.now();
            addLog(`Medium text (${res.data.total_words} words): ${((t1 - t0) / 1000).toFixed(4)} sec`);

            t0 = performance.now();
            res = await api.post("/api/analyze", { text: long_text });
            t1 = performance.now();
            addLog(`Long text (${res.data.total_words} words): ${((t1 - t0) / 1000).toFixed(4)} sec`);

            addLog("### – Search Operations Test");
            const search_terms = ["a", "ab", "abc", "test", "nonexistent", "cat"];
            for (const term of search_terms) {
                t0 = performance.now();
                const searchRes = await api.get("/api/search", { params: { query: term } });
                t1 = performance.now();
                addLog(`Search '${term}': ${((t1 - t0) / 1000).toFixed(4)} sec, found: ${searchRes.data.length}`);
            }

            addLog("### – Statistics & POS Test");
            t0 = performance.now();
            const statsRes = await api.get("/api/statistics");
            t1 = performance.now();
            addLog(`Statistics & POS aggregation: ${((t1 - t0) / 1000).toFixed(4)} sec`);
            if (statsRes.data?.pos_distribution) {
                addLog(`Tokens aggregated: NOUN(${statsRes.data.pos_distribution.NOUN || 0}), VERB(${statsRes.data.pos_distribution.VERB || 0})`);
            }

            addLog("### – Concordance Test");
            t0 = performance.now();
            const kwicRes = await api.get("/api/concordance/kwic", { params: { lemma: "cat", window: 5 } });
            t1 = performance.now();
            addLog(`KWIC generation (lemma 'cat', window 5): ${((t1 - t0) / 1000).toFixed(4)} sec, contexts: ${kwicRes.data.length}`);

            t0 = performance.now();
            const colRes = await api.get("/api/concordance/collocates", { params: { lemma: "cat", window: 5 } });
            t1 = performance.now();
            addLog(`Collocates (lemma 'cat', window 5): ${((t1 - t0) / 1000).toFixed(4)} sec, unique: ${Object.keys(colRes.data || {}).length}`);

            addLog("✅ Performance Test Completed Successfully!");

        } catch (err) {
            console.error(err);
            addLog(`❌ Error during test: ${err.message}`);
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <Clock className="title-icon" size={24} /> Performance Testing
            </h2>

            <div style={{ backgroundColor: 'var(--surface-hover)', padding: '1.5rem', borderRadius: '8px', marginBottom: '2rem' }}>
                <h4 style={{ color: 'var(--primary)', marginBottom: '0.5rem' }}>Specification</h4>
                <ul style={{ margin: 0, color: 'var(--text-muted)' }}>
                    <li><strong>NLP Engine:</strong> spaCy (en_core_web_sm)</li>
                    <li><strong>Database:</strong> SQLite via SQLAlchemy</li>
                    <li><strong>API:</strong> FastAPI / Uvicorn</li>
                    <li><strong>Frontend:</strong> React Vite Single Page App</li>
                </ul>
            </div>

            <button onClick={runTest} disabled={isRunning} style={{ marginBottom: '2rem' }}>
                <Clock size={18} className={isRunning ? 'animate-spin' : ''} />
                {isRunning ? 'Running Tests...' : 'Run Performance Benchmark'}
            </button>

            {results.length > 0 && (
                <div className="animate-fade-in" style={{ backgroundColor: '#000', color: '#0f0', padding: '1rem', borderRadius: '8px', fontFamily: 'monospace', lineHeight: '1.8' }}>
                    {results.map((line, idx) => {
                        const isHeader = line.startsWith('###');
                        const isSuccess = line.startsWith('✅');
                        const isError = line.startsWith('❌');

                        return (
                            <div
                                key={idx}
                                style={{
                                    color: isHeader ? '#fff' : isSuccess ? '#0f0' : isError ? '#f00' : '#0f0',
                                    fontWeight: isHeader ? 'bold' : 'normal',
                                    marginTop: isHeader ? '1rem' : '0'
                                }}
                            >
                                {line}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
