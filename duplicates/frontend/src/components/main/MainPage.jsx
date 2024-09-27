import React from 'react';
import "./style.css";
import FileUploader from "../file_uploader/FileUploader";
import VideoPlayer from "../videoPlayer/VideoPlayer";

const DOC_TYPES_CACHE = {};

class MainPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            originalVideoUrl: null,
            imageURL: null,
            loading: false,
            isExampleModalOpen: false,
            isTypeModalOpen: false,
            responseData: {},
            currentDocType: '', // Assuming this is required
            files: [],
        };
    }

    componentDidMount() {
        fetch(`${process.env.REACT_APP_BACKEND}/handle`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error');
                }
                return response.json();
            })
            .then(data => {
                // Handle initial data if needed
                this.setState({});
            })
            .catch(error => {
                this.setState({})
            });
    }

    setFiles = (files) => {
        this.setState({ files: files });
        console.log("Files loaded: ", this.state.files);
    }

    setResponse = (data) => {
        this.setState({ responseData: data })
    }

    // Function to handle local file upload
    sendLocalFile = async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doctype', this.state.currentDocType);

        console.log("File uploaded: ", file);

        const config = {
            method: 'POST',
            body: formData,
        };

        try {
            this.setState({ loading: true });
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/upload`, config);
            if (response.ok) {
                const data = await response.json();
                this.setResponse(data);
                // Handle the response data as needed
            } else {
                console.error('Error uploading file:', response.statusText);
            }
            // Optionally update state or props as needed
        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            this.setState({ loading: false });
        }
    }

    // Function to handle video URL submission
    sendFileFromWeb = async (videoUrl) => {
        console.log("File uploaded: ", videoUrl);


        const data = {
            videoUrl: videoUrl,
            doctype: this.state.currentDocType,
        };

        const config = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        };

        try {
            this.setState({ loading: true });
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/upload-link`, config);
            if (response.ok) {
                const responseData = await response.json();
                this.setResponse(responseData);
                // Handle the response data as needed
            } else {
                console.error('Error uploading link:', response.statusText);
            }
            // Optionally update state or props as needed
        } catch (error) {
            alert('Сервер недоступен');
        } finally {
            this.setState({ loading: false });
        }
    }

    handleVideoUrlSubmit = (url) => {
        this.setState({ originalVideoUrl: url });
    }

    render() {
        const { loading, originalVideoUrl, responseData } = this.state;
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
                    />

                    {originalVideoUrl &&
                        <VideoPlayer src={originalVideoUrl}></VideoPlayer>
                    }
                    {loading && (
                        <div className="big-center loader"></div>
                    )}
                </div>
            </div>
        );
    }
}

export default MainPage;
