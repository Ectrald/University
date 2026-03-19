import React, { useEffect, useRef } from 'react';

export default function ContextMenu({ x, y, onClose, onEdit, onDelete }) {
    const menuRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                onClose();
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, [onClose]);

    return (
        <div
            ref={menuRef}
            className="context-menu"
            style={{ top: y, left: x }}
        >
            <div className="context-menu-item" onClick={onEdit}>
                <span style={{ fontSize: '1.2rem' }}>✏️</span> Edit Metadata
            </div>
            <div className="context-menu-item danger" onClick={onDelete}>
                <span style={{ fontSize: '1.2rem' }}>🗑️</span> Delete Text
            </div>
        </div>
    );
}
