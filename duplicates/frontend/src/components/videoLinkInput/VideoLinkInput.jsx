import React from 'react';
import yappySvg from '../../img/yappy.svg';

class VideoLinkInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            videoUrl: ''
        };
    }

    handleChange(event) {
        this.setState({ videoUrl: event.target.value });
    }

    handleSubmit() {
        this.props.onVideoUrlSubmit(this.state.videoUrl);
    }


    render() {
        return (
            <div className="link-input-container">
                <div className="link-input-header">
                    <h1>Вставьте <span className="text-warning">ссылку</span> на видео <span className="yappy">Yappy</span>
                    </h1>

                </div>

                <input
                    type="text"
                    placeholder="Введите ссылку на видео"
                    value={this.state.videoUrl}
                    onChange={(e) => this.handleChange(e)}
                />
                <button className="btn btn-primary" onClick={() => this.handleSubmit()}>Отправить</button>
            </div>
        );
    }
}

export default VideoLinkInput;
