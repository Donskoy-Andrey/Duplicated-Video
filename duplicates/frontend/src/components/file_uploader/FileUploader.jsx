import React, {useState, useRef} from 'react';
import OverlayTrigger from 'react-bootstrap/OverlayTrigger';
import Popover from 'react-bootstrap/Popover';

const FileUploader = (props) => {
    const allowedFormats = ['pdf', 'docx', 'xlsx', 'txt', 'rtf'];
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const fileInputRef = useRef(null);
    const docs_number = 1;

    const handleFileChange = (e) => {
        // console.log('supertest ', selectedFiles === e.target.files);
        setSelectedFiles([...selectedFiles, ...e.target.files]);
        // console.log('selected files: ', e.target.files[0]);
    };


    const checkFiles = (files) => {
        if (!(files && files.length)) {
            alert("Загрузите файлы")
            return false;
        }

        if (files.length !== docs_number) {
            alert(`неверное количество документов (должно быть ${docs_number})`)
            return false;
        }

        for (let i = 0; i < files.length; i++) {
            const extension = files[i].name.split('.').pop().toLowerCase();
            if (!allowedFormats.includes(extension)) {
                alert("Неверный формат файла")
                return false;
            }
        }
        return true;
    }

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const files = [...e.dataTransfer.files];
        setSelectedFiles([...selectedFiles, ...files]);
    };

    const handleUpload = async () => {
        const formData = new FormData();
        console.log('currentDocType:', props.currentDocType);

        if (!checkFiles(selectedFiles)) {
            return;
        }
        for (let i = 0; i < selectedFiles.length; i++) {
            formData.append('files', selectedFiles[i]);
        }
        formData.append('doctype', props.currentDocType);


        const config = {
            method: 'POST',
            body: formData,
        };

        try {
            props.setResponse({});
            setLoading(true);
            const response = await fetch(`${process.env.REACT_APP_BACKEND}/upload`, config);
            if (response.ok) {
                const data = await response.json(); // Await the response.json() promise
                props.setResponse(data);
                setSelectedFiles([]);
            } else {
                console.error('Error uploading files:', response.statusText, response.error, response.message, response.content);
            }
            props.setFiles(selectedFiles);
            setSelectedFiles([]);
            fileInputRef.current.value = ''
        } catch (error) {
            alert("backend is disabled");
        } finally {
            setLoading(false);
        }
    };

    const checkFileFormat = (file) => {
        const extension = file.name.split('.').pop().toLowerCase();
        return allowedFormats.includes(extension);
    }

    const handleClick = () => {
        fileInputRef.current.click();
    };

    const deleteFile = (index) => {
        const updatedFiles = [...selectedFiles];
        updatedFiles.splice(index, 1);
        setSelectedFiles(updatedFiles);
    };

    const renderPopover = (title, content) => (
        <Popover>
            <Popover.Header>{title}</Popover.Header>
            <Popover.Body>{content}</Popover.Body>
        </Popover>
    );

    const popoverContent = `Допустимые форматы: 
    pdf, 
    doc, 
    docx, 
    xlsx, 
    txt, 
    rtf`;

    return (


        <div>
            <div
                onClick={handleClick}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                className="drag-drop-field"
            >
                <i className="fa-regular fa-file-lines fa-big"></i>
                <h3>Перетащите файл{docs_number > 1 ? `ы (${docs_number} шт.)` : ''} сюда <br/>или <div
                    className="text-warning">выберите {docs_number > 1 ? `их` : 'его'} вручную</div></h3>
                <div className="drag-drop-field__extensions">pdf, docx, xlsx, txt, rtf</div>
                <input
                    type="file"
                    multiple
                    onInput={handleFileChange}
                    ref={fileInputRef}
                    style={{display: 'none'}}
                />
            </div>

            <div className="input-control__buttons">
                <button className="btn btn-primary" onClick={handleUpload}>Отправить</button>
                <button className="btn btn-success modal-button" onClick={props.openModal}>Примеры запросов</button>
            </div>
            {loading && (
                <div className="big-center loader"></div>
            )}
            <div className="uploaded-file__container">
                {selectedFiles.length > 0 && (
                    selectedFiles.map((file, i) => (
                        <div className={`uploaded-file__item ${checkFileFormat(file) ? "" : "wrong"}`} key={i}>
                            {checkFileFormat(file) ? (
                                <span className="uploaded-file__filename">{file.name.length > 15 ? `${file.name.substring(0, 5)}...${file.name.substring(file.name.length - 10)}` : file.name}</span>
                            ) : (
                                <OverlayTrigger
                                    trigger={['hover', 'focus']}
                                    placement="top"
                                    overlay={renderPopover('Неверный формат', popoverContent)}
                                >
                                    <span>{file.name}</span>
                                </OverlayTrigger>
                            )}
                            <button className="btn btn-close-white uploaded-file__button" onClick={() => deleteFile(i)}>x</button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default FileUploader;