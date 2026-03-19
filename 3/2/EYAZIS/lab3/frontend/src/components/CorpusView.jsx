import React, { useState, useEffect } from 'react';
import { Upload, Plus, RefreshCw, Trash2, Edit3, X } from 'lucide-react';
import api from '../api';
import ContextMenu from './ContextMenu';

export default function CorpusView() {
    const [texts, setTexts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    // Context Menu State
    const [contextMenu, setContextMenu] = useState(null); // { x, y, textId }

    // Edit Modal State
    const [editDoc, setEditDoc] = useState(null);

    // Add Form State
    const [addForm, setAddForm] = useState({ title: '', content: '', author: '', genre: '', date_created: '' });

    // Upload Form State
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadMeta, setUploadMeta] = useState({ title: '', author: '', genre: '', date_created: '' });

    const fetchTexts = async () => {
        setIsLoading(true);
        try {
            const { data } = await api.get('/api/texts');
            setTexts(data);
        } catch (err) {
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTexts();
    }, []);

    const handleContextMenu = (e, textId) => {
        e.preventDefault();
        setContextMenu({ x: e.clientX, y: e.clientY, textId });
    };

    const handleCloseContextMenu = () => {
        setContextMenu(null);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this text?")) return;
        try {
            await api.delete(`/api/texts/${id}`);
            fetchTexts();
        } catch (e) {
            console.error(e);
            alert('Failed to delete text');
        }
    };

    const handleEdit = (text) => {
        setEditDoc(text);
    };

    const submitEdit = async (e) => {
        e.preventDefault();
        try {
            await api.put(`/api/texts/${editDoc.id}`, {
                title: editDoc.title,
                author: editDoc.author,
                genre: editDoc.genre,
                date_created: editDoc.date_created,
            });
            setEditDoc(null);
            fetchTexts();
        } catch (error) {
            console.error(error);
            alert('Failed to update text');
        }
    };

    const submitAddText = async (e) => {
        e.preventDefault();
        try {
            await api.post('/api/texts', { ...addForm, domain: 'Animals' });
            setAddForm({ title: '', content: '', author: '', genre: '', date_created: '' });
            fetchTexts();
        } catch (error) {
            console.error(error);
            alert('Failed to add text');
        }
    };

    const submitUpload = async (e) => {
        e.preventDefault();
        if (!uploadFile) return;
        const formData = new FormData();
        formData.append('file', uploadFile);
        if (uploadMeta.title) formData.append('title', uploadMeta.title);
        if (uploadMeta.author) formData.append('author', uploadMeta.author);
        if (uploadMeta.genre) formData.append('genre', uploadMeta.genre);
        if (uploadMeta.date_created) formData.append('date_created', uploadMeta.date_created);
        formData.append('domain', 'Animals');

        try {
            await api.post('/api/texts/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setUploadFile(null);
            setUploadMeta({ title: '', author: '', genre: '', date_created: '' });
            e.target.reset();
            fetchTexts();
        } catch (error) {
            console.error(error);
            alert('Failed to upload file');
        }
    };

    return (
        <div>
            <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h2>Texts in Corpus</h2>
                    <button onClick={fetchTexts} disabled={isLoading} className="secondary">
                        <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} /> Refresh
                    </button>
                </div>

                {texts.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)' }}>Corpus is empty. Add texts below.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Title</th>
                                    <th>Words</th>
                                    <th>Domain</th>
                                    <th>Author</th>
                                    <th>Genre</th>
                                    <th>Created</th>
                                </tr>
                            </thead>
                            <tbody>
                                {texts.map(t => (
                                    <tr
                                        key={t.id}
                                        onContextMenu={(e) => handleContextMenu(e, t.id)}
                                        style={{ cursor: 'context-menu' }}
                                        title="Right-click for options"
                                    >
                                        <td>{t.id}</td>
                                        <td><strong style={{ color: 'var(--primary)' }}>{t.title}</strong></td>
                                        <td>{t.word_count}</td>
                                        <td>{t.domain}</td>
                                        <td>{t.author || '-'}</td>
                                        <td>{t.genre || '-'}</td>
                                        <td>{t.date_created || '-'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem' }}>
                <div className="card">
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                        <Plus size={20} className="title-icon" /> Add Text Manually
                    </h3>
                    <form onSubmit={submitAddText}>
                        <input
                            placeholder="Title (Optional)"
                            value={addForm.title}
                            onChange={e => setAddForm({ ...addForm, title: e.target.value })}
                        />
                        <textarea
                            placeholder="Content *"
                            required
                            rows={5}
                            value={addForm.content}
                            onChange={e => setAddForm({ ...addForm, content: e.target.value })}
                        />
                        <div className="form-grid">
                            <input
                                placeholder="Author"
                                value={addForm.author}
                                onChange={e => setAddForm({ ...addForm, author: e.target.value })}
                            />
                            <input
                                placeholder="Genre"
                                value={addForm.genre}
                                onChange={e => setAddForm({ ...addForm, genre: e.target.value })}
                            />
                            <input
                                placeholder="Date (YYYY-MM-DD)"
                                value={addForm.date_created}
                                onChange={e => setAddForm({ ...addForm, date_created: e.target.value })}
                            />
                        </div>
                        <button type="submit" style={{ marginTop: '1rem' }}><Plus size={16} /> Add Text</button>
                    </form>
                </div>

                <div className="card">
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                        <Upload size={20} className="title-icon" /> Upload File
                    </h3>
                    <form onSubmit={submitUpload}>
                        <input
                            type="file"
                            required
                            onChange={e => setUploadFile(e.target.files[0])}
                            style={{ backgroundColor: 'transparent', padding: '0.5rem 0' }}
                        />
                        <input
                            placeholder="Title (Optional, defaults to filename)"
                            value={uploadMeta.title}
                            onChange={e => setUploadMeta({ ...uploadMeta, title: e.target.value })}
                        />
                        <div className="form-grid">
                            <input
                                placeholder="Author"
                                value={uploadMeta.author}
                                onChange={e => setUploadMeta({ ...uploadMeta, author: e.target.value })}
                            />
                            <input
                                placeholder="Genre"
                                value={uploadMeta.genre}
                                onChange={e => setUploadMeta({ ...uploadMeta, genre: e.target.value })}
                            />
                            <input
                                placeholder="Date"
                                value={uploadMeta.date_created}
                                onChange={e => setUploadMeta({ ...uploadMeta, date_created: e.target.value })}
                            />
                        </div>
                        <button type="submit" style={{ marginTop: '1rem' }}><Upload size={16} /> Upload</button>
                    </form>
                </div>
            </div>

            {contextMenu && (
                <ContextMenu
                    x={contextMenu.x}
                    y={contextMenu.y}
                    onClose={handleCloseContextMenu}
                    onEdit={() => {
                        handleEdit(texts.find(t => t.id === contextMenu.textId));
                        handleCloseContextMenu();
                    }}
                    onDelete={() => {
                        handleDelete(contextMenu.textId);
                        handleCloseContextMenu();
                    }}
                />
            )}

            {editDoc && (
                <div className="modal-overlay" onClick={(e) => { if (e.target.classList.contains('modal-overlay')) setEditDoc(null); }}>
                    <div className="modal-content">
                        <div className="modal-header">
                            <h3>Edit Metadata (ID: {editDoc.id})</h3>
                            <button type="button" className="close-btn" onClick={() => setEditDoc(null)}><X size={24} /></button>
                        </div>
                        <form onSubmit={submitEdit}>
                            <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Title</label>
                            <input
                                value={editDoc.title}
                                onChange={e => setEditDoc({ ...editDoc, title: e.target.value })}
                            />
                            <div className="form-grid">
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Author</label>
                                    <input
                                        value={editDoc.author}
                                        onChange={e => setEditDoc({ ...editDoc, author: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Genre</label>
                                    <input
                                        value={editDoc.genre}
                                        onChange={e => setEditDoc({ ...editDoc, genre: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text-muted)' }}>Date</label>
                                    <input
                                        value={editDoc.date_created}
                                        onChange={e => setEditDoc({ ...editDoc, date_created: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
                                <button type="submit"><Edit3 size={16} /> Save Changes</button>
                                <button type="button" className="secondary" onClick={() => setEditDoc(null)}>Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
