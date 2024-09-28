import React from 'react';
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";
import ResponseInfo from "../responseInfo/ResponseInfo";
import ServerErrorToast from "../serverErrorToast/ServerErrorToast"; // Импортируем новый компонент

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

    setShowToast = (value) => {
        this.setState({ showToast: value });
    }

    setErrorCode = (value) => {
        this.setState({ errorCode: value });
    }

    setErrorMessage = (value) => {
        this.setState({ errorMessage: value });
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

    // Загрузка файла на бэкенд
    uploadFileToBackend = async (file) => {
        try {
            this.setState({ loading: true });
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${process.env.REACT_APP_BACKEND}/test_file`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
            }

            const responseData = await response.json();
            this.setResponse(responseData);
            // this.setShowToast(true);

        } catch (error) {
            this.setState({
                errorCode: error.message,
                errorMessage: "Произошла ошибка при отправке файла"
            });
            // this.setShowToast(true);
        } finally {
            this.setState({ loading: false });
        }
    }

    // Отправка URL на бэкенд
    uploadUrlToBackend = async (videoUrl) => {
        try {
            this.setState({ loading: true });

            const response = await fetch(`${process.env.REACT_APP_BACKEND}/test_url`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: videoUrl })
            });

            if (!response.ok) {
                throw new Error(`Ошибка ${response.status}: ${response.statusText}`);
            }

            const responseData = await response.json();
            this.setResponse(responseData);
            this.setShowToast(true);

        } catch (error) {
            this.setState({
                errorCode: error.message,
                errorMessage: "Произошла ошибка при отправке URL"
            });
            // this.setShowToast(true);
        } finally {
            this.setState({ loading: false });
        }
    }

    render() {
        const { loading, originalVideoUrl, responseData, showToast, errorCode, errorMessage } = this.state;
        const { is_duplicate, duplicate_for, link_duplicate } = responseData;

        return (
            <div className="main-page">
                <div className="container mt-4 main-bg">
                    <svg xmlns="http://www.w3.org/2000/svg" className="d-none">
                        <symbol id="exclamation-triangle-fill" viewBox="0 0 16 16">
                            <path
                                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                        </symbol>
                    </svg>

                    <div className="main-header"></div>

                    <FileUploader
                        sendLocalFile={this.sendLocalFile}
                        sendFileFromWeb={this.sendFileFromWeb}
                        setFiles={this.setFiles}
                        currentDocType={this.state.currentDocType}
                        setResponse={this.setResponse}
                        responseData={responseData}
                        loading={loading}
                        onValidVideoUrl={this.handleValidVideoUrl}
                        onInValidVideoUrl={this.handleInValidVideoUrl}
                    />

                    <div className="videos-container">
                        {originalVideoUrl && (
                            <div>
                                <h3>Оригинальное видео:</h3>
                                <VideoPlayer src={originalVideoUrl} />
                            </div>
                        )}

                        {loading && (
                            <div className="big-center loader"></div>
                        )}

                        {link_duplicate && (
                            <div>
                                <h3>Видео из ответа сервера:</h3>
                                <VideoPlayer src={link_duplicate} />
                            </div>
                        )}
                    </div>

                    {/* Компонент для отображения информации об ответе или ошибке */}
                    {!loading && showToast && (
                        <ResponseInfo
                            showToast={showToast}
                            setShowToast={this.setShowToast}
                            is_duplicate={is_duplicate}
                            duplicate_for={duplicate_for}
                            link_duplicate={link_duplicate}
                        />

                    )}
                    {!loading && errorCode && (
                        <ServerErrorToast
                            setShowToast={this.setShowToast}
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
