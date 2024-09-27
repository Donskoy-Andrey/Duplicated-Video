import React from 'react';

const ResponseInfo = ({ is_duplicate, duplicate_for, link_duplicate }) => {
    return (
        <div
            className={`response-message ${
                is_duplicate ? 'response-error' : 'response-success'
            }`}
        >
            {is_duplicate ? (
                <div>
                    <h4>Дубликат найден</h4>
                    <p>ID: <code>{duplicate_for}</code></p>
                    <p>
                        <a href={link_duplicate} target="_blank" rel="noopener noreferrer">
                            Открыть по ссылку
                        </a>
                    </p>
                </div>
            ) : (
                <p>Видео уникально и успешно загружено.</p>
            )}
        </div>
    );
};

export default ResponseInfo;
