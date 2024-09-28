import React, { useState, useRef, useEffect } from 'react';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Popover from 'react-bootstrap/Popover';
import { ReportButton } from "../reportButton/ReportButton";

const FileUploader = (props) => {
    const {
        onValidVideoUrl,
        sendLocalFile,
        sendFileFromWeb,
        loading,
        link_duplicate,
        confidenceLevel,
        setConfidenceLevel
    } = props;

    const allowedFormats = ['mp4', 'wav'];
    const [selectedFile, setSelectedFile] = useState(null);
    const [videoUrl, setVideoUrl] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isUrlValid, setIsUrlValid] = useState(false);
    const [isFileValid, setIsFileValid] = useState(false);
    const [isCheckingUrl, setIsCheckingUrl] = useState(false);
    const fileInputRef = useRef(null);

    useEffect(() => {
        updateSliderBackground();
    }, [confidenceLevel]);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setSelectedFile(file);
        setVideoUrl('');
        setErrorMessage('');
        setIsUrlValid(false);
        validateFile(file);
        if (onValidVideoUrl) {
            onValidVideoUrl(null);
        }
    };

    const handleLinkChange = async (e) => {
        const url = e.target.value;
        setVideoUrl(url);
        setSelectedFile(null);
        setErrorMessage('');
        setIsFileValid(false);

        if (url === '') {
            setIsUrlValid(false);
            if (onValidVideoUrl) {
                onValidVideoUrl(null);
            }
            return;
        }

        console.log(url);

        setIsCheckingUrl(true);
        const isValid = await validateUrl(url);
        setIsCheckingUrl(false);

        if (!isValid) {
            setIsUrlValid(false);
            if (onValidVideoUrl) {
                onValidVideoUrl(null);
            }
        } else {
            setIsUrlValid(true);
            if (onValidVideoUrl) {
                onValidVideoUrl(url);
            }
        }
    };

    const validateFile = (file) => {
        if (!file) {
            setIsFileValid(false);
            return false;
        }

        const extension = file.name.split('.').pop().toLowerCase();
        if (!allowedFormats.includes(extension)) {
            setIsFileValid(false);
            setErrorMessage('Недопустимый формат файла. Допустимые форматы: mp4, wav.');
            return false;
        }
        setIsFileValid(true);
        setErrorMessage('');
        return true;
    };

    const validateUrl = (url) => {
        return new Promise((resolve) => {
            try {
                const parsedUrl = new URL(url);
                const hostname = parsedUrl.hostname.toLowerCase();

                // Проверяем, что домен - s3.ritm.media
                if (hostname === 's3.ritm.media') {
                    // Проверяем, что URL оканчивается на '.mp4'
                    if (parsedUrl.pathname.endsWith('.mp4')) {
                        // Создаем элемент video
                        const video = document.createElement('video');

                        // Обработчик успешной загрузки метаданных видео
                        video.onloadedmetadata = () => {
                            resolve(true);
                        };

                        // Обработчик ошибки загрузки видео
                        video.onerror = () => {
                            setErrorMessage('Файл не найден по указанному URL.');
                            resolve(false);
                        };

                        // Устанавливаем источник видео
                        video.src = url;

                        video.load();

                    } else {
                        setErrorMessage('Ссылка должна вести на файл с расширением .mp4.');
                        resolve(false);
                    }
                } else {
                    setErrorMessage('Домен ссылки должен быть s3.ritm.media.');
                    resolve(false);
                }
            } catch (e) {
                setErrorMessage('Введите корректный URL.');
                resolve(false);
            }
        });
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const file = e.dataTransfer.files[0];
        setSelectedFile(file);
        setVideoUrl('');
        setErrorMessage('');
        setIsUrlValid(false);
        validateFile(file);
        if (onValidVideoUrl) {
            onValidVideoUrl(null);
        }
    };

    const handleUpload = () => {
        if (selectedFile && isFileValid) {
            sendLocalFile(selectedFile);
        } else if (videoUrl && isUrlValid) {
            sendFileFromWeb(videoUrl);
        } else {
            setErrorMessage('Загрузите файл или введите корректную ссылку');
        }
    };

    const checkFileFormat = (file) => {
        const extension = file.name.split('.').pop().toLowerCase();
        return allowedFormats.includes(extension);
    };

    const handleClick = () => {
        fileInputRef.current.click();
    };

    const deleteFile = () => {
        setSelectedFile(null);
        setErrorMessage('');
        setIsFileValid(false);
    };

    const renderPopover = (title, content) => (
        <Popover>
            <Popover.Header>{title}</Popover.Header>
            <Popover.Body>{content}</Popover.Body>
        </Popover>
    );

    const popoverContent = `Допустимые форматы: mp4, wav`;

    // Handler for slider change
    const handleSliderChange = (e) => {
        const value = parseFloat(e.target.value);
        setConfidenceLevel(value);
    };

    // Handler for input field change
    const handleInputChange = (e) => {
        let value = parseFloat(e.target.value);
        if (isNaN(value)) {
            value = '';
        } else {
            // Clamp the value between 0.8 and 0.99
            value = Math.min(Math.max(value, 0.8), 0.99);
        }
        setConfidenceLevel(value);
    };

    // Функция для обновления фона слайдера
    const updateSliderBackground = () => {
        const slider = document.querySelector('.confidence-slider');
        if (slider) {
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);
            const value = parseFloat(slider.value);
            const percentage = ((value - min) / (max - min)) * 100;
            // Устанавливаем градиентный фон: желтый до ползунка, #2c3034 после
            slider.style.background = `linear-gradient(to right, #f4c142 0%, #f4c142 ${percentage}%, #2c3034 ${percentage}%, #2c3034 100%)`;
        }
    };

    return (
        <div>
            <div
                onClick={handleClick}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="drag-drop-field"
            >
                <i className="fa-regular fa-file-lines fa-big"></i>
                <h3>
                    Перетащите видео файл сюда <br />
                    или <div className="text-warning">выберите его вручную</div>
                </h3>
                <div className="drag-drop-field__extensions">mp4, wav</div>
                <input
                    type="file"
                    onInput={handleFileChange}
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                />
            </div>

            <div className="link-input-container">
                <h3>
                    Или вставьте <span className="text-warning">ссылку</span> на видео{' '}
                    <span className="yappy">Yappy</span>
                </h3>
                <div className="link-input-field">
                    <input
                        type="text"
                        placeholder="Введите ссылку на видео"
                        value={videoUrl}
                        onChange={handleLinkChange}
                    />
                    {isCheckingUrl && <span className="loader-text"></span>}
                </div>
            </div>

            {/* Confidence Level Section */}
            <div className="confidence-level-container" style={{ marginTop: '20px' }}>
                <h3>
                    Настройте уровень <span className="text-warning">уверенности</span> модели
                </h3>
                <div className="confidence-level-controls" style={{ display: 'flex', alignItems: 'center' }}>
                    <input
                        type="range"
                        min="0.8"
                        max="0.99"
                        step="0.01"
                        value={confidenceLevel}
                        onChange={handleSliderChange}
                        className="confidence-slider"
                        aria-label="Уровень уверенности"
                    />
                    <input
                        type="number"
                        min="0.8"
                        max="0.99"
                        step="0.01"
                        value={confidenceLevel}
                        onChange={handleInputChange}
                        className="confidence-number"
                        aria-label="Уровень уверенности"
                    />
                </div>

            </div>
            {/* End of Confidence Level Section */}

            <div className="input-control__buttons" style={{ marginTop: '20px' }}>
                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={loading || (!isFileValid && !isUrlValid) || isCheckingUrl}
                >
                    Отправить
                </button>
                {link_duplicate && <ReportButton />}
            </div>
            {errorMessage && <p className="error-message">{errorMessage}</p>}
            <div className="uploaded-file__container">
                {selectedFile && (
                    <div
                        className={`uploaded-file__item ${
                            checkFileFormat(selectedFile) ? '' : 'wrong'
                        }`}
                    >
                        {checkFileFormat(selectedFile) ? (
                            <span className="uploaded-file__filename">
                                {selectedFile.name.length > 15
                                    ? `${selectedFile.name.substring(0, 5)}...${selectedFile.name.substring(
                                        selectedFile.name.length - 10
                                    )}`
                                    : selectedFile.name}
                            </span>
                        ) : (
                            <OverlayTrigger
                                trigger={['hover', 'focus']}
                                placement="top"
                                overlay={renderPopover('Неверный формат', popoverContent)}
                            >
                                <span>{selectedFile.name}</span>
                            </OverlayTrigger>
                        )}
                        <button className="btn btn-close-white uploaded-file__button" onClick={deleteFile}>
                            x
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUploader;
