import React, { useState } from 'react';
import { Book, Search, BarChart2, FileText, Activity, HelpCircle, BookOpen, Clock, GitBranch } from 'lucide-react';
import CorpusView from './components/CorpusView';
import SearchView from './components/SearchView';
import StatisticsView from './components/StatisticsView';
import ConcordanceView from './components/ConcordanceView';
import AnalyzeView from './components/AnalyzeView';
import HelpView from './components/HelpView';
import TheoryView from './components/TheoryView';
import TestingView from './components/TestingView';
import SyntaxView from './components/SyntaxView';

function App() {
    const [activeTab, setActiveTab] = useState('corpus');

    const tabs = [
        { id: 'corpus', label: 'Corpus', icon: Book },
        { id: 'search', label: 'Search', icon: Search },
        { id: 'stats', label: 'Statistics', icon: BarChart2 },
        { id: 'conc', label: 'Concordance', icon: FileText },
        { id: 'analyze', label: 'Analyze', icon: Activity },
        { id: 'syntax', label: 'Syntax', icon: GitBranch },
        { id: 'help', label: 'Help', icon: HelpCircle },
        { id: 'theory', label: 'Theory', icon: BookOpen },
        { id: 'testing', label: 'Testing', icon: Clock },
    ];

    return (
        <div>
            <h1 className="title">
                <BookOpen className="title-icon" size={32} />
                Corpus Manager
            </h1>

            <div className="tabs">
                {tabs.map(tab => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => setActiveTab(tab.id)}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Icon size={18} />
                                {tab.label}
                            </div>
                        </button>
                    );
                })}
            </div>

            <div className="animate-fade-in">
                {activeTab === 'corpus' && <CorpusView />}
                {activeTab === 'search' && <SearchView />}
                {activeTab === 'stats' && <StatisticsView />}
                {activeTab === 'conc' && <ConcordanceView />}
                {activeTab === 'analyze' && <AnalyzeView />}
                {activeTab === 'syntax' && <SyntaxView />}
                {activeTab === 'help' && <HelpView />}
                {activeTab === 'theory' && <TheoryView />}
                {activeTab === 'testing' && <TestingView />}
            </div>
        </div>
    );
}

export default App;
