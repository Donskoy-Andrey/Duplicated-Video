import React, { useState, useRef } from 'react';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Popover from 'react-bootstrap/Popover';

const FileUploader = (props) => {
    const allowedFormats = ['mp4', 'wav'];
    const [selectedFile, setSelectedFile] = useState(null);
    const [videoUrl, setVideoUrl] = useState('');
    const [errorMessage, setErrorMessage] = useState('');
    const [isUrlValid, setIsUrlValid] = useState(false);
    const [isFileValid, setIsFileValid] = useState(false); // New state for file validity
    const [isCheckingUrl, setIsCheckingUrl] = useState(false);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setSelectedFile(file);
        setVideoUrl('');
        setErrorMessage('');
        setIsUrlValid(false);
        validateFile(file); // Validate the selected file
        if (props.onValidVideoUrl) {
            props.onValidVideoUrl(null); // Clear video preview in MainPage
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
            if (props.onValidVideoUrl) {
                props.onValidVideoUrl(null);
            }
            return;
        }

        console.log(url);

        setIsCheckingUrl(true);
        const isValid = await validateUrl(url);
        setIsCheckingUrl(false);

        if (!isValid) {
            setIsUrlValid(false);
            if (props.onValidVideoUrl) {
                props.onValidVideoUrl(null);
            }
        } else {
            setIsUrlValid(true);
            if (props.onValidVideoUrl) {
                props.onValidVideoUrl(url);
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
            return false;
        }
        setIsFileValid(true);
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
        validateFile(file); // Validate the dropped file
        if (props.onValidVideoUrl) {
            props.onValidVideoUrl(null); // Clear video preview in MainPage
        }
    };

    const handleUpload = () => {
        if (selectedFile && isFileValid) {
            props.sendLocalFile(selectedFile);
        } else if (videoUrl && isUrlValid) {
            props.sendFileFromWeb(videoUrl);
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
                    Перетащите видео файл сюда <br/>
                    или <div className="text-warning">выберите его вручную</div>
                </h3>
                <div className="drag-drop-field__extensions">mp4, wav</div>
                <input
                    type="file"
                    onInput={handleFileChange}
                    ref={fileInputRef}
                    style={{display: 'none'}}
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

            <div className="input-control__buttons">
                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={props.loading || (!isFileValid && !isUrlValid) || isCheckingUrl}
                >
                    Отправить
                </button>
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
