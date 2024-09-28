import React from 'react';
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";
import ResponseInfo from "../responseInfo/ResponseInfo";
import ServerErrorToast from "../serverErrorToast/ServerErrorToast";

const REACT_APP_BACKEND = "http://localhost/api";

class MainPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            originalVideoUrl: null,
            uploadedFile: null,
            loading: false,
            showToast: false,
            responseData: {},
            currentDocType: '',
            confidenceLevel: 0.97,
            files: [],
            errorCode: null,
            errorMessage: null,
            uid: null // добавлен новый state для UID
        };
        this.resultPollingInterval = null; // Интервал для опроса
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

    // Функция для получения результата с сервера по UID
    getResultFromBackend = async (uid) => {
        try {
            const response = await fetch(`${REACT_APP_BACKEND}/get-result`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ uid })
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();

            if (Object.keys(data).length === 0) {
                console.log("Результат еще не готов. Повторный запрос...");
                return;
            }

            clearInterval(this.resultPollingInterval); // Останавливаем опрос, если получили результат
            this.setResponse(data);
            this.setShowToast(true);

        } catch (error) {
            clearInterval(this.resultPollingInterval); // Останавливаем опрос при ошибке
            this.setState({
                errorCode: error.response?.status || '500',
                errorMessage: error.message || "Произошла ошибка при получении результата"
            });
        }
    }

    // Новая функция для отправки локального файла на сервер
    uploadFileToBackend = async (file) => {
        try {
            this.setShowToast(false);
            this.setState({ loading: true });

            const formData = new FormData();
            formData.append('file', file);
            formData.append('confidenceLevel', this.state.confidenceLevel);

            const response = await fetch(`${REACT_APP_BACKEND}/upload-file`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`Ошибка сервера: ${response.status}`);
            }

            const data = await response.json();
            this.setState({ uid: data.uid });

            // Начинаем опрос сервера для получения результата
            this.resultPollingInterval = setInterval(() => {
                this.getResultFromBackend(data.uid);
            }, 2000); // Интервал опроса 2 секунды

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

            const payload = {
                "link": videoUrl,
                "confidenceLevel": this.state.confidenceLevel
            };

            // const response = await fetch(`${REACT_APP_BACKEND}/upload-link`, {
            //     method: 'POST',
            //     headers: {
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify(payload),
            // });
            //
            // if (!response.ok) {
            //     throw new Error(`Ошибка сервера: ${response.status}`);
            // }
            //
            // const data = await response.json();
            const data = {uid: 'sdfsdfsd'}
            this.setState({ uid: data.uid });

            // Начинаем опрос сервера для получения результата
            this.resultPollingInterval = setInterval(() => {
                this.getResultFromBackend(data.uid);
            }, 2000);

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
        await this.uploadFileToBackend(file);
    }

    sendFileFromWeb = async (videoUrl) => {
        this.setResponse({});
        console.log("Загруженный URL видео: ", videoUrl);
        this.setState({ originalVideoUrl: videoUrl });
        await this.uploadUrlToBackend(videoUrl);
    }

    handleValidVideoUrl = (url) => {
        console.log('validVideoUrl', url);
        this.setState({ originalVideoUrl: url });
    };

    handleInValidVideoUrl = () => {
        this.setState({ originalVideoUrl: null });
    };

    componentWillUnmount() {
        // Очищаем интервал при размонтировании компонента
        if (this.resultPollingInterval) {
            clearInterval(this.resultPollingInterval);
        }
    }

    render() {
        const { loading, originalVideoUrl, responseData, showToast, errorCode, errorMessage, confidenceLevel } = this.state;
        const { is_duplicate, link_duplicate } = responseData;

        return (
            <div className="main-page">
                <div className="container mt-4 main-bg">
                    {/* Ваш остальной JSX-код, включая заголовок и компоненты */}

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
