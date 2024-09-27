import React from 'react';
import "./style.css";
import FileUploader from "../file_uploader/FileUploader";
import {Categories} from "../categories/Categories";
import VideoLinkInput from "../videoLinkInput/VideoLinkInput";

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
            responseData: {}
        };
    }

    componentDidMount() {
        fetch(`${process.env.REACT_APP_BACKEND}/"handle"`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Server error');
                }
                return response.json();
            })
            .then(data => {
                // console.log("init data: ", data);
                this.setState({}); // Set the fetched data to state
            })
            .catch(error => {
                // console.error('Error fetching data:', error);
                // alert('backend is disabled'); // Display alert for status 500 error
                this.setState({})
            });
    }


    setFiles = (files) => {
        this.setState({files: files});
    }


    setResponse = (data) => {
        this.setState({responseData: data})
    }

    handleVideoUrlSubmit(url) {
        this.setState({ originalVideoUrl: url });
        // Здесь вы можете добавить дополнительную логику, например, валидацию ссылки или запрос к серверу
    }

    render() {
        const {loading, isExampleModalOpen, responseData} = this.state;
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


                    </div>

                    {/*<FileUploader*/}
                    {/*    setFiles={this.setFiles}*/}
                    {/*    currentDocType={this.state.currentDocType}*/}
                    {/*    setResponse={this.setResponse}*/}
                    {/*    responseData={responseData}*/}
                    {/*/>*/}

                    <VideoLinkInput onVideoUrlSubmit={(url) => this.handleVideoUrlSubmit(url)} />


                    {loading && (
                        <div className="big-center loader"></div>
                    )}

                </div>
            </div>
        );
    }
}

export default MainPage;