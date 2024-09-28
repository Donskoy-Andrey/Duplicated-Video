import React from 'react';
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";
import ResponseInfo from "../responseInfo/ResponseInfo";
import ServerErrorToast from "../serverErrorToast/ServerErrorToast";

const REACT_APP_BACKEND = 'backend:8000/';

class MainPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            originalVideoUrl: null, // URL или локальный объект оригинального видео
            uploadedFile: null,     // Локальный объект файла при загрузке
            loading: false,         // Флаг состояния загрузки
            showToast: false,       // Флаг отображения уведомления
            responseData: {},       // Данные ответа сервера
            currentDocType: '',     // Текущий тип документа (если требуется)
            confidenceLevel: 0.97,  // Уровень уверенности модели
            files: [],              // Массив файлов
            errorCode: null,        // Код ошибки сервера
            errorMessage: null      // Сообщение ошибки сервера
        };
    }

    componentDidMount() {
        // Дополнительные действия после монтирования компонента (если необходимо)
    }

    setFiles = (files) => {
        this.setState({ files: files });
        console.log("Загруженные файлы: ", this.state.files);
    }

    setResponse = (data) => {
        this.setState({ responseData: data });
    }

    setConfidenceLevel = (confidenceLevel) => {
        if (confidenceLevel >= 0.8 || confidenceLevel <= 0.99) {}
        this.setState({ confidenceLevel: confidenceLevel });
    }

    setShowToast = (value) => {
        this.setState({ showToast: value });
    }

    setErrorCode = (value) => {
        this.setState({ errorCode: value });
    }

    setErrorMessage = (value) => {
        this.setState({ errorMessage: value });
    }

    // Новая функция для отправки локального файла на сервер
    uploadFileToBackend = async (file) => {
        try {
            this.setState({ loading: true });

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${REACT_APP_BACKEND}/file_upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            // Предполагается, что ответ сервера содержит is_duplicate, duplicate_for, link_duplicate
            this.setResponse(data);
            this.setShowToast(true);
        } catch (error) {
            this.setState({
                errorCode: error.response?.status || '500',
                errorMessage: error.message || "Произошла ошибка при отправке файла",
            });
        } finally {
            this.setState({ loading: false });
        }
    }

    // Новая функция для отправки URL на сервер
    uploadUrlToBackend = async (videoUrl) => {
        try {
            this.setState({ loading: true });

            const response = await fetch(`${REACT_APP_BACKEND}/link_upload`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ videoUrl }),
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            this.setResponse(data);
            this.setShowToast(true);
        } catch (error) {
            this.setState({
                errorCode: error.response?.status || '500',
                errorMessage: error.message || "Произошла ошибка при отправке URL",
            });
        } finally {
            this.setState({ loading: false });
        }
    }

    sendLocalFile = async (file) => {
        this.setResponse({});
        const fileUrl = URL.createObjectURL(file);
        this.setState({ originalVideoUrl: fileUrl, uploadedFile: file });
        // await this.uploadFileToBackend(file);
        // Если нужно использовать моковую функцию вместо настоящей, раскомментируйте следующую строку:
        await this.mockUploadFileToBackend(file);
    }

    sendFileFromWeb = async (videoUrl) => {
        this.setResponse({});
        console.log("Загруженный URL видео: ", videoUrl);
        this.setState({ originalVideoUrl: videoUrl });
        // await this.uploadUrlToBackend(videoUrl);
        // Если нужно использовать моковую функцию вместо настоящей, раскомментируйте следующую строку:
        await this.mockUploadUrlToBackend(videoUrl);
    }

    handleValidVideoUrl = (url) => {
        console.log('validVideoUrl', url);
        this.setState({ originalVideoUrl: url });
    };

    handleInValidVideoUrl = () => {
        this.setState({ originalVideoUrl: null });
    };

    // Мок-функция для загрузки файла
    mockUploadFileToBackend = async (file) => {
        try {
            this.setState({ loading: true });

            // Имитируем задержку обработки
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Симуляция успешного ответа
            const mockResponse = {
                is_duplicate: Math.random() < 0.5,      // Случайное определение, является ли видео дубликатом
                link_duplicate: "https://s3.ritm.media/yappy-db-duplicates/4182b2d2-4264-41dd-b101-4c1c66f4bdab.mp4"
            };

            if (!mockResponse.is_duplicate) {
                mockResponse.link_duplicate = null;
            }

            this.setResponse(mockResponse);
            this.setShowToast(true);

        } catch (error) {
            this.setState({
                errorCode: '500',
                errorMessage: "Произошла ошибка при имитации отправки файла"
            });
        } finally {
            this.setState({ loading: false });
        }
    }

    // Мок-функция для отправки URL
    mockUploadUrlToBackend = async (videoUrl) => {
        try {
            this.setState({ loading: true });

            // Имитируем задержку обработки
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Симуляция успешного ответа
            const mockResponse = {
                is_duplicate: Math.random() < 0.5,      // Случайное определение, является ли видео дубликатом
                link_duplicate: "https://s3.ritm.media/yappy-db-duplicates/4182b2d2-4264-41dd-b101-4c1c66f4bdab.mp4"
            };

            if (!mockResponse.is_duplicate) {
                mockResponse.link_duplicate = null;
            }

            this.setResponse(mockResponse);
            this.setShowToast(true);

        } catch (error) {
            this.setState({
                errorCode: '500',
                errorMessage: "Произошла ошибка при имитации отправки URL"
            });
        } finally {
            this.setState({ loading: false });
        }
    }

    render() {
        const { loading, originalVideoUrl, responseData, showToast, errorCode, errorMessage, confidenceLevel } = this.state;
        const { is_duplicate, link_duplicate } = responseData;

        return (
            <div className="main-page">
                <div className="container mt-4 main-bg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="d-none">
                        <symbol id="exclamation-triangle-fill" viewBox="0 0 16 16">
                            <path
                                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                        </symbol>
                    </svg>

                    <div className="main-header">
                        <h1>
                            Поиск дубликатов видео <br />
                            <span className="text-warning"> AAA IT</span> для <span className="yappy">Yappy</span>
                        </h1>
                    </div>

                    <FileUploader
                        sendLocalFile={this.sendLocalFile}
                        confidenceLevel={confidenceLevel}
                        setConfidenceLevel={this.setConfidenceLevel}
                        sendFileFromWeb={this.sendFileFromWeb}
                        setFiles={this.setFiles}
                        currentDocType={this.state.currentDocType}
                        setResponse={this.setResponse}
                        responseData={responseData}
                        loading={loading}
                        onValidVideoUrl={this.handleValidVideoUrl}
                        onInValidVideoUrl={this.handleInValidVideoUrl}
                        link_duplicate={this.state.responseData.link_duplicate}
                    />

                    <div className="videos-container">
                        {originalVideoUrl && (
                            <div className="video-card">
                                <h3>Ваше видео:</h3>
                                <VideoPlayer src={originalVideoUrl} />
                            </div>
                        )}

                        {loading && (
                            <div className="big-center loader"></div>
                        )}

                        {link_duplicate && (
                            <div className="video-card">
                                <h3>Дубликат:</h3>
                                <VideoPlayer src={link_duplicate} />
                            </div>
                        )}
                    </div>

                    {!loading && showToast && (
                        <ResponseInfo
                            showToast={showToast}
                            setShowToast={this.setShowToast}
                            is_duplicate={is_duplicate}
                            link_duplicate={link_duplicate}
                        />
                    )}
                    {!loading && errorCode && (
                        <ServerErrorToast
                            errorCode={errorCode}
                            errorMessage={errorMessage}
                            setErrorCode={this.setErrorCode}
                            setErrorMessage={this.setErrorMessage}
                        />
                    )}
                </div>
            </div>
        );
    }
}

export default MainPage;
