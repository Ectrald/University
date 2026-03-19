import React from 'react';
import { HelpCircle } from 'lucide-react';

export default function HelpView() {
    return (
        <div className="card">
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
                <HelpCircle className="title-icon" size={24} /> Руководство пользователя
            </h2>
            <div style={{ lineHeight: '1.6', color: 'var(--text)' }}>
                <p>Добро пожаловать в <strong>Corpus Manager</strong>! Данное приложение предназначено для работы с корпусом текстов на английском языке в предметной области «Животные» (вариант 16).</p>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>1. Вкладка "Corpus" (Корпус)</h3>
                <p>Здесь вы управляете коллекцией ваших текстов.</p>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Добавление текстов:</strong> Вы можете ввести текст вручную или загрузить файл (TXT, RTF, PDF, DOC, DOCX).</li>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Контекстное меню:</strong> Кликните ПРАВОЙ КНОПКОЙ МЫШИ на строке с текстом, чтобы отредактировать метаданные или удалить текст.</li>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Очистка:</strong> Кнопка "Clear Corpus" полностью удалит все тексты из базы данных.</li>
                </ul>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>2. Вкладка "Search" (Поиск)</h3>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}>Позволяет найти конкретное слово или лемму во всем корпусе.</li>
                    <li style={{ marginBottom: '0.5rem' }}>Поиск работает побуквенно (character-by-character) — результаты появляются по мере ввода без необходимости нажимать "Enter".</li>
                    <li style={{ marginBottom: '0.5rem' }}>При наличии результатов появляется фильтр по частям речи (POS).</li>
                </ul>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>3. Вкладка "Statistics" (Статистика)</h3>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}>Показывает общую частотную статистику по всему корпусу.</li>
                    <li style={{ marginBottom: '0.5rem' }}>Отображает интерактивные графики распределения частей речи и топ самых часто используемых слов.</li>
                </ul>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>4. Вкладка "Concordance" (Конкорданс)</h3>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}><strong>KWIC (Key Word in Context):</strong> Позволяет увидеть искомое слово (лемму) в его естественном окружении. Укажите лемму и размер окна. Искомая лемма будет выделена цветом.</li>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Collocates (Коллокаты):</strong> Показывает частоту слов, встречающихся рядом с искомым словом.</li>
                </ul>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>5. Вкладка "Analyze" (Анализ)</h3>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}>Позволяет проанализировать любой текст "на лету", без сохранения его в базу данных. Полезно для быстрой проверки внешних текстов.</li>
                    <li style={{ marginBottom: '0.5rem' }}>Выводит графики распределения частей речи и частот слов "на лету" без перезагрузки всей страницы.</li>
                </ul>

                <h3 style={{ marginTop: '2rem', color: 'var(--primary)' }}>6. Вкладка "Syntax Tree" (Синтаксический анализ)</h3>
                <ul>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Анализ предложений:</strong> Выберите текст из корпуса для автоматического построения синтаксического дерева (зависимости слов).</li>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Редактирование:</strong> Нажмите "Edit", чтобы вручную изменить метки связей (Dependency), части речи (POS) или указать другой ID главного слова (Head ID). Не забудьте сохранить изменения.</li>
                    <li style={{ marginBottom: '0.5rem' }}><strong>Экспорт:</strong> Результаты синтаксического анализа можно экспортировать в формате JSON для дальнейшего документирования.</li>
                </ul>
            </div>
        </div>

    );
}
