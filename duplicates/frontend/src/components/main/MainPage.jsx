import React from 'react';
import "./style.css";
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";
import ResponseInfo from "../responseInfo/ResponseInfo"; // Import the new component

class MainPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            originalVideoUrl: null, // URL or local object URL of the original video
            uploadedFile: null,     // Local file object if a file is uploaded
            loading: false,
            showToast: false,
            responseData: {},
            currentDocType: '', // Assuming this is required
            files: [],
        };
    }

    componentDidMount() {
        this.setState({});
    }

    setFiles = (files) => {
        this.setState({ files: files });
        console.log("Files loaded: ", this.state.files);
    }

    setResponse = (data) => {
        this.setState({ responseData: data })
    }

    setShowToast = (value) => {
        this.setState({showToast: value});
    }


    // Function to handle local file upload
    sendLocalFile = async (file) => {
        this.setResponse({});
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doctype', this.state.currentDocType);

        console.log("File uploaded: ", file);

        // Create a local URL for the uploaded file to display it
        const fileUrl = URL.createObjectURL(file);
        this.setState({ originalVideoUrl: fileUrl, uploadedFile: file });

        // Mocking the server response
        try {
            this.setState({ loading: true });

            // Simulate a delay to mimic server processing time
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mocked response data without 'message' field
            const mockResponse = {
                is_duplicate: Math.random() < 0.5 ? true : false, // Randomly decide if it's a duplicate
                duplicate_for: "1234567890abcdef", // Mocked duplicate ID
                link_duplicate: "https://s3.ritm.media/yappy-db-duplicates/4182b2d2-4264-41dd-b101-4c1c66f4bdab.mp4"
                // 'message' field is removed
            };

            // If not a duplicate, set duplicate_for and link_duplicate to null
            if (!mockResponse.is_duplicate) {
                mockResponse.duplicate_for = null;
                mockResponse.link_duplicate = null;
            }

            // Set the response data
            this.setResponse(mockResponse);
            this.setShowToast(true);

            console.log("Mocked server response:", mockResponse);

        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            this.setState({ loading: false });
        }
    }

    // Function to handle video URL submission
    sendFileFromWeb = async (videoUrl) => {
        this.setResponse({});
        console.log("File uploaded: ", videoUrl);

        // Set the original video URL to display it
        this.setState({ originalVideoUrl: videoUrl });

        // Mocking the server response
        try {
            this.setState({ loading: true });

            // Simulate a delay to mimic server processing time
            await new Promise(resolve => setTimeout(resolve, 1000));

            // Mocked response data without 'message' field
            const mockResponse = {
                is_duplicate: Math.random() < 0.5 ? true : false, // Randomly decide if it's a duplicate
                duplicate_for: "1234567890abcdef", // Mocked duplicate ID
                link_duplicate: "https://s3.ritm.media/yappy-db-duplicates/4182b2d2-4264-41dd-b101-4c1c66f4bdab.mp4"
                // 'message' field is removed
            };

            // If not a duplicate, set duplicate_for and link_duplicate to null
            if (!mockResponse.is_duplicate) {
                mockResponse.duplicate_for = null;
                mockResponse.link_duplicate = null;
            }

            // Set the response data
            this.setResponse(mockResponse);
            this.setShowToast(true);

            console.log("Mocked server response:", mockResponse);

        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            this.setState({ loading: false });
        }
    }

    handleValidVideoUrl = (url) => {
        this.setState({ originalVideoUrl: url });
    };

    render() {
        const { loading, originalVideoUrl, responseData, showToast } = this.state;

        // Destructure responseData for easier access
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
                    <div className="main-header">
                        {/* Add header content if needed */}
                    </div>

                    <FileUploader
                        sendLocalFile={this.sendLocalFile}
                        sendFileFromWeb={this.sendFileFromWeb}
                        setFiles={this.setFiles}
                        currentDocType={this.state.currentDocType}
                        setResponse={this.setResponse}
                        responseData={responseData}
                        loading={loading}
                        onValidVideoUrl={this.handleValidVideoUrl}
                    />

                    <div className="videos-container">
                    {/* Original Video Player */}
                    {originalVideoUrl &&
                        <div>
                            <h3>Оригинальное видео:</h3>
                            <VideoPlayer src={originalVideoUrl}></VideoPlayer>
                        </div>
                    }

                    {loading && (
                        <div className="big-center loader"></div>
                    )}
                    {/* Video Player for the response link */}
                    {responseData.link_duplicate &&
                        <div>
                            <h3>Видео из ответа сервера:</h3>
                            <VideoPlayer src={responseData.link_duplicate}></VideoPlayer>
                        </div>
                    }
                    </div>


                    {/* Use the new ResponseMessage component */}
                    {!loading && showToast && (
                        <ResponseInfo
                            showToast={this.state.showToast}
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
