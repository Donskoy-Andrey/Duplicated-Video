// src/components/VideoPlayer.js
import hackLogo from './hack.png';
import yappyLogo from './yappy.svg';
import React, {useRef, useState, useEffect} from 'react';
import './style.css'; // Измененный путь к стилям

const VideoPlayer = ({src, poster}) => {
    const videoRef = useRef(null);
    const hideControlsTimeout = useRef(null);
    const progressRef = useRef(null);
    const volumeRef = useRef(null);


    const [isPlaying, setIsPlaying] = useState(false);
    const [showCentralControls, setShowCentralControls] = useState(true); // Для отображения центральных кнопок
    const [progress, setProgress] = useState(0); // Прогресс в процентах
    const [currentTime, setCurrentTime] = useState(0); // Текущее время в секундах
    const [duration, setDuration] = useState(0); // Длительность видео в секундах
    const [volume, setVolume] = useState(1); // Громкость (от 0 до 1)
    const [isMuted, setIsMuted] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isHorizontal, setIsHorizontal] = useState(true);
    const [isPiPSupported, setIsPiPSupported] = useState(false);


    // Обработчик воспроизведения/паузы
    const togglePlayPause = () => {
        const video = videoRef.current;
        if (!video) return;

        if (isPlaying) {
            video.pause();
        } else {
            video.play();
        }
    };

    // Обработчик клика на видео
    const handleVideoClick = () => {
        togglePlayPause();
        setShowCentralControls(true);

        // Clear any existing timeout
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current);
        }

        // Set a new timeout to hide controls after 1.5 seconds
        hideControlsTimeout.current = setTimeout(() => {
            setShowCentralControls(false);
        }, 1500);
    };

    const handleMouseMove = () => {
        setShowCentralControls(true);

        // Clear any existing timeout
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current);
        }

        // Set a new timeout to hide controls after 1.5 seconds of inactivity
        hideControlsTimeout.current = setTimeout(() => {
            setShowCentralControls(false);
        }, 1500);
    };

    const handleLoadedMetadata = () => {
        const video = videoRef.current;
        if (!video) return;

        setDuration(video.duration);
        setCurrentTime(video.currentTime);

        // Определение ориентации видео
        if (video.videoWidth >= video.videoHeight) {
            setIsHorizontal(true); // Горизонтальное видео
        } else {
            setIsHorizontal(false); // Вертикальное видео
        }
    };

    const togglePictureInPicture = async () => {
        const video = videoRef.current;
        if (!video) return;

        try {
            if (document.pictureInPictureElement) {
                await document.exitPictureInPicture();
            } else {
                await video.requestPictureInPicture();
            }
        } catch (error) {
            console.error('Ошибка при переключении режима "Картинка в картинке":', error);
        }
    };


    // Перемотка назад на 10 секунд
    const rewind10 = (e) => {
        e.stopPropagation(); // Предотвращение всплытия события клика
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.max(video.currentTime - 10, 0);
        setProgress((video.currentTime / video.duration) * 100);
        setShowCentralControls(true);
        setTimeout(() => {
            setShowCentralControls(false);
        }, 1500);
    };

    // Перемотка вперед на 10 секунд
    const forward10 = (e) => {
        e.stopPropagation(); // Предотвращение всплытия события клика
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.min(video.currentTime + 10, video.duration);
        setProgress((video.currentTime / video.duration) * 100);
        setShowCentralControls(true);
        setTimeout(() => {
            setShowCentralControls(false);
        }, 1500);
    };

    // Обновление состояния при воспроизведении
    const handlePlay = () => {
        setIsPlaying(true);
    };

    // Обновление состояния при паузе
    const handlePause = () => {
        setIsPlaying(false);
    };

    // Обновление прогресса
    const handleTimeUpdate = () => {
        const video = videoRef.current;
        if (!video) return;

        const current = video.currentTime;
        const total = video.duration;

        setCurrentTime(current);
        setDuration(total);
        const progressValue = (current / total) * 100;
        setProgress(progressValue);

        // Обновляем CSS-переменную
        if (progressRef.current) {
            progressRef.current.style.setProperty('--progress-value', `${progressValue}%`);
        }
    };

    // Перемотка видео через полосу прогресса
    const handleProgressChange = (e) => {
        const video = videoRef.current;
        if (!video) return;

        const newProgress = e.target.value;
        const newTime = (newProgress / 100) * duration;
        video.currentTime = newTime;
        setProgress(newProgress);

        // Обновляем CSS-переменную
        if (progressRef.current) {
            progressRef.current.style.setProperty('--progress-value', `${newProgress}%`);
        }
    };

// Обновление громкости
    const handleVolumeChange = (e) => {
        const video = videoRef.current;
        if (!video) return;

        const newVolume = e.target.value;
        video.volume = newVolume;
        setVolume(newVolume);
        setIsMuted(newVolume === 0);

        // Обновляем CSS-переменную
        if (volumeRef.current) {
            const volumeValue = (newVolume - e.target.min) / (e.target.max - e.target.min) * 100;
            volumeRef.current.style.setProperty('--volume-value', `${volumeValue}%`);
        }
    };

    // Включение/выключение звука
    const toggleMute = () => {
        const video = videoRef.current;
        if (!video) return;

        video.muted = !isMuted;
        setIsMuted(!isMuted);
    };

    // Переключение полноэкранного режима
    const toggleFullscreen = () => {
        const videoContainer = videoRef.current.parentElement;

        if (!document.fullscreenElement) {
            videoContainer.requestFullscreen().catch(err => {
                console.error(`Ошибка при попытке включить полноэкранный режим: ${err.message}`);
            });
            setIsFullscreen(true);
        } else {
            document.exitFullscreen();
            setIsFullscreen(false);
        }
    };

    // Форматирование времени (например, 00:00)
    const formatTime = (time) => {
        if (isNaN(time)) return '00:00';
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    };

    // Обработчик клавиатурных сокращений
    useEffect(() => {
        const handleKeyDown = (e) => {
            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    togglePlayPause();
                    break;
                case 'ArrowRight':
                    forward10(e);
                    break;
                case 'ArrowLeft':
                    rewind10(e);
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
                case 'm':
                case 'M':
                    toggleMute();
                    break;
                default:
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyDown);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [isPlaying, isMuted, isFullscreen]); // Зависимости

    // Обработчики событий видео
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        video.addEventListener('play', handlePlay);
        video.addEventListener('pause', handlePause);
        video.addEventListener('timeupdate', handleTimeUpdate);
        video.addEventListener('loadedmetadata', handleLoadedMetadata);

        return () => {
            video.removeEventListener('play', handlePlay);
            video.removeEventListener('pause', handlePause);
            video.removeEventListener('timeupdate', handleTimeUpdate);
            video.removeEventListener('loadedmetadata', handleLoadedMetadata);
        };
    }, [duration]);
    useEffect(() => {
        setIsPiPSupported('pictureInPictureEnabled' in document);
    }, []);

    // Обработчики наведения мыши
    const handleMouseEnter = () => {
        setShowCentralControls(true);

        // Clear any existing timeout
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current);
        }
    };

    const handleMouseLeave = () => {
        // Clear any existing timeout
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current);
        }

        // Hide the controls immediately or after a delay
        setShowCentralControls(false);
    };

    useEffect(() => {
        if (progressRef.current) {
            progressRef.current.style.setProperty('--progress-value', `${progress}%`);
        }
        if (volumeRef.current) {
            const volumeValue = (volume - volumeRef.current.min) / (volumeRef.current.max - volumeRef.current.min) * 100;
            volumeRef.current.style.setProperty('--volume-value', `${volumeValue}%`);
        }
    }, []);

    return (
        <div
            className={`video-container ${isHorizontal ? 'horizontal-video' : 'vertical-video'} ${
                showCentralControls ? 'show-controls' : ''
            }`}
            onClick={handleVideoClick}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onMouseMove={handleMouseMove}
        >
            <video ref={videoRef} src={src} poster={poster} className="video"/>

            {/* Заголовок */}
            <div className="video-header" onClick={(e) => e.stopPropagation()}>
                <span>AAA IT для</span>
                <img src={hackLogo} alt="Hack" className="header-logo"/>
                <img src={yappyLogo} alt="Yappy" className="header-logo"/>
            </div>

            {/* Центральные кнопки управления (всегда рендерятся) */}
            <div className="central-controls">
                <button
                    onClick={rewind10}
                    className="central-button rewind-button"
                    aria-label="Перемотать назад на 10 секунд"
                >
                    <i className="fa-solid fa-backward"></i>
                </button>
                <button
                    onClick={togglePlayPause}
                    className="central-button play-pause-button"
                    aria-label={isPlaying ? 'Пауза' : 'Воспроизведение'}
                >
                    {isPlaying ? (
                        <i className="fa-solid fa-pause"></i>
                    ) : (
                        <i className="fa-solid fa-play"></i>
                    )}
                </button>
                <button
                    onClick={forward10}
                    className="central-button forward-button"
                    aria-label="Перемотать вперед на 10 секунд"
                >
                    <i className="fa-solid fa-forward"></i>
                </button>
            </div>

            {/* Панель управления (всегда рендерится) */}
            <div className="controls" onClick={(e) => e.stopPropagation()}>
                {/* Полоса прогресса */}
                <div className="progress-container">
                    <span className="time">{formatTime(currentTime)}</span>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={progress}
                        onChange={handleProgressChange}
                        className="progress-bar"
                        ref={progressRef}
                    />
                    <span className="time">{formatTime(duration)}</span>
                </div>

                {/* Правая часть элементов управления */}
                <div className="right-controls">
                    <button
                        onClick={toggleMute}
                        className="control-button"
                        aria-label={isMuted || volume === 0 ? 'Включить звук' : 'Выключить звук'}
                    >
                        {isMuted || volume === 0 ? (
                            <i className="fa-solid fa-volume-xmark white"></i>
                        ) : (
                            <i className="fa-solid fa-volume-high white"></i>
                        )}
                    </button>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        onChange={handleVolumeChange}
                        className="volume-slider"
                        ref={volumeRef}
                    />
                    {isPiPSupported && (
                        <button
                            onClick={togglePictureInPicture}
                            className="control-button"
                            aria-label="Картинка в картинке"
                        >
                            <i className="fa-solid fa-up-right-from-square white"></i>
                        </button>
                    )}
                    <button
                        onClick={toggleFullscreen}
                        className="control-button"
                        aria-label={
                            isFullscreen ? 'Выйти из полноэкранного режима' : 'Войти в полноэкранный режим'
                        }
                    >
                        {isFullscreen ? (
                            <i className="fa-solid fa-compress white"></i>
                        ) : (
                            <i className="fa-solid fa-expand white"></i>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}


export default VideoPlayer;
