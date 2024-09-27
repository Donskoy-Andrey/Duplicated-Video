import React from 'react';
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";
import ResponseInfo from "../responseInfo/ResponseInfo"; // Импортируем новый компонент

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
        };
    }

    componentDidMount() {
        // Дополнительные действия после монтирования компонента (если необходимо)
    }

    // Устанавливаем файлы в состояние
    setFiles = (files) => {
        this.setState({ files: files });
        console.log("Загруженные файлы: ", this.state.files);
    }

    // Устанавливаем данные ответа сервера в состояние
    setResponse = (data) => {
        this.setState({ responseData: data });
    }

    // Управляем отображением уведомления
    setShowToast = (value) => {
        this.setState({ showToast: value });
    }

    // Функция для обработки загрузки локального файла
    sendLocalFile = async (file) => {
        this.setResponse({});

        // Создаем локальный URL для отображения загруженного видео
        const fileUrl = URL.createObjectURL(file);
        this.setState({ originalVideoUrl: fileUrl, uploadedFile: file });

        // Вызываем функцию для имитации ответа сервера
        await this.mockServerResponse();
    }

    // Функция для обработки отправки видео по URL
    sendFileFromWeb = async (videoUrl) => {
        this.setResponse({});

        console.log("Загруженный URL видео: ", videoUrl);

        // Устанавливаем оригинальный URL видео для отображения
        this.setState({ originalVideoUrl: videoUrl });

        // Вызываем функцию для имитации ответа сервера
        await this.mockServerResponse();
    }

    // Обрабатываем валидный URL видео
    handleValidVideoUrl = (url) => {
        console.log('validVideoUrl', url);
        this.setState({ originalVideoUrl: url });
    };

    handleInValidVideoUrl = () => {
        this.setState({ originalVideoUrl: null });
    };

    // Функция для имитации ответа сервера
    mockServerResponse = async () => {
        try {
            this.setState({ loading: true });

            // Имитируем задержку, чтобы смоделировать время обработки сервера
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Смоделированный ответ сервера
            const mockResponse = {
                is_duplicate: Math.random() < 0.5,      // Случайное определение, является ли видео дубликатом
                duplicate_for: "1234567890abcdef",      // Идентификатор дубликата
                link_duplicate: "https://s3.ritm.media/yappy-db-duplicates/4182b2d2-4264-41dd-b101-4c1c66f4bdab.mp4"
            };

            // Если видео не является дубликатом, очищаем соответствующие поля
            if (!mockResponse.is_duplicate) {
                mockResponse.duplicate_for = null;
                mockResponse.link_duplicate = null;
            }

            // Устанавливаем данные ответа сервера
            this.setResponse(mockResponse);
            this.setShowToast(true);


        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            this.setState({ loading: false });
        }
    }

    render() {
        const { loading, originalVideoUrl, responseData, showToast } = this.state;

        // Деструктурируем данные ответа для удобства
        const { is_duplicate, duplicate_for, link_duplicate } = responseData;

        return (
            <div className="main-page">
                <div className="container mt-4 main-bg">
                    {/* Скрытый SVG для иконки уведомления */}
                    <svg xmlns="http://www.w3.org/2000/svg" className="d-none">
                        <symbol id="exclamation-triangle-fill" viewBox="0 0 16 16">
                            <path
                                d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                        </symbol>
                    </svg>

                    <div className="main-header">
                        {/* Здесь можно добавить заголовок при необходимости */}
                    </div>

                    {/* Компонент загрузчика файлов */}
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
                        {/* Плеер для оригинального видео */}
                        {originalVideoUrl && (
                            <div>
                                <h3>Оригинальное видео:</h3>
                                <VideoPlayer src={originalVideoUrl} />
                            </div>
                        )}

                        {/* Индикатор загрузки */}
                        {loading && (
                            <div className="big-center loader"></div>
                        )}

                        {/* Плеер для видео из ответа сервера */}
                        {link_duplicate && (
                            <div>
                                <h3>Видео из ответа сервера:</h3>
                                <VideoPlayer src={link_duplicate} />
                            </div>
                        )}
                    </div>

                    {/* Компонент для отображения информации об ответе */}
                    {!loading && showToast && (
                        <ResponseInfo
                            showToast={showToast}
                            setShowToast={this.setShowToast}
                            is_duplicate={is_duplicate}
                            duplicate_for={duplicate_for}
                            link_duplicate={link_duplicate}
                        />
                    )}
                </div>
            </div>
        );
    }
}

export default MainPage;
