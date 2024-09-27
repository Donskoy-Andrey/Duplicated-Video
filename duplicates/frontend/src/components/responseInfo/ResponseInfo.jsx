// ResponseInfo.js
import React, {useEffect} from 'react';

const ResponseInfo = ({showToast, setShowToast, is_duplicate, duplicate_for, link_duplicate}) => {
    const onClose = () => {
        setShowToast(false);
    };

    useEffect(() => {
        const toastElement = document.querySelector('.custom-toast');
        setTimeout(() => {
            toastElement.classList.add('show');
        }, 100); // Добавляем задержку для анимации
    }, []);

    return (
        <div
            className={`custom-toast ${is_duplicate ? 'toast-error' : 'toast-success'}`}
            onClick={onClose}
        >
            <button className="toast-close-button" onClick={onClose} aria-label="Закрыть">
                &times;
            </button>
            {is_duplicate ? (
                <div>
                    <h4 className="toast-header">Дубликат найден</h4>
                </div>
            ) : (
                <div>
                    <h4 className="toast-header">Дубликат не найден</h4>
                </div>
            )}
        </div>
    );
};

export default ResponseInfo;
