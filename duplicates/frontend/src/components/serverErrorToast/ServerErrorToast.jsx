// ResponseInfo.js
import React, {useEffect} from 'react';

const ServerErrorToast = ({setShowToast, errorCode, errorMessage, setErrorCode, setErrorMessage}) => {
    const onClose = () => {
        // setShowToast(false);
        setErrorCode(null);
        setErrorMessage(null);
    };

    useEffect(() => {
        const toastElement = document.querySelector('.custom-toast');
        setTimeout(() => {
            toastElement.classList.add('show');
        }, 100); // Добавляем задержку для анимации
    }, []);

    return (
        <div
            className={`custom-toast toast-error`}
            onClick={onClose}
        >
            <button className="toast-close-button" onClick={onClose} aria-label="Закрыть">
                &times;
            </button>
                <div>
                    <h4 className="toast-header">Ошибка обработки</h4>
                    <p>{errorCode}: {errorMessage}</p>
                </div>
        </div>
    );
};

export default ServerErrorToast;
