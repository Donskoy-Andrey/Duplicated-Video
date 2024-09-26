import React, { useRef, useState } from 'react';

const ZipUploadComponent = ({ docsNumber, openModal }) => {
    const fileInputRef = useRef(null);
    const [uploadedFile, setUploadedFile] = useState(null);
    const [outputFile, setOutputFile] = useState(null);
    const [filename, setFilename] = useState("");
    const [loading, setLoading] = useState(false);

    const maxFileSize = 10 * 1024 * 1024;
    const handleClick = () => {
        fileInputRef.current.click();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const files = event.dataTransfer.files;
        handleFileChange(files);
    };

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleFileChange = (files) => {
        const file = files[0];
        if (file.size > maxFileSize) {
            alert(`File ${file.name} exceeds the maximum file size of 20MB`);
            return; // Skip appending this file
        }

        setUploadedFile(files[0]);
        setFilename(files[0].name); // Set the filename
    }

    const handleUpload = async () => {
        const formData = new FormData();
        setLoading(true);
        formData.append('file', uploadedFile); // Using the uploadedFile state

        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/upload_zip`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                throw new Error('Failed to upload file');
            }
            const blob = await response.blob(); // Assuming the server returns the processed zip file
            console.log(blob);
            setOutputFile(blob); // Set the output file received from the server
        } catch (error) {
            alert("backend is disabled");
        }finally {
            setLoading(false);
        }
    };

    const handleExample = async () => {
        const requestData = { example: 'first' };
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/zip_example_handle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json' // Specify content type as JSON
                },
                body: JSON.stringify(requestData) // Convert JSON object to string
            });
            if (!response.ok) {
                throw new Error('Failed to upload file');
            }
            const blob = await response.blob(); // Assuming the server returns the processed zip file
            console.log(blob);
            setOutputFile(blob); // Set the output file received from the server
        } catch (error) {
            alert("Backend is disabled");
        } finally {
            setLoading(false);
        }
    }


    const handleDownload = () => {
        if (outputFile) {
            const url = window.URL.createObjectURL(outputFile);
            const link = document.createElement('a');
            link.href = url;
            if (uploadedFile) {
                link.setAttribute('download', `processed_${uploadedFile.name}`);
            }
            else{
                link.setAttribute('download', 'processed.zip');
            }
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
        }
    };

    return (
        <div className="main-page">
            <div className="container mt-4 main-bg">
                <svg xmlns="http://www.w3.org/2000/svg" className="d-none">
                    <symbol id="exclamation-triangle-fill" viewBox="0 0 16 16">
                        <path
                            d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                    </symbol>
                </svg>

                <div
                    onClick={handleClick}
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    className="drag-drop-field"
                >
                    <i className="fa-regular fa-file-lines fa-big"></i>
                    <h3>
                        Перетащите zip файл сюда <br/>
                        или <div className="text-warning">выберите его вручную</div>
                    </h3>
                    <div className="drag-drop-field__extensions">{uploadedFile ? uploadedFile.name : 'zip'}</div>
                    <input
                        type="file"
                        accept=".zip"
                        onChange={(e) => handleFileChange(e.target.files)}
                        ref={fileInputRef}
                        style={{display: 'none'}}
                    />
                </div>

                <div className="input-control__buttons">
                    <button className="btn btn-primary" onClick={handleUpload}>
                        Отправить
                    </button>
                    {outputFile && (
                        <div>
                            <button className="btn btn-primary" onClick={handleDownload}>
                                Скачать
                            </button>
                        </div>
                    )}
                    <button className="btn btn-success modal-button" onClick={handleExample}>Пример запроса</button>

                </div>
                {loading && (
                    <div className="big-center loader"></div>
                )}
            </div>
        </div>
    );
};

export default ZipUploadComponent;
