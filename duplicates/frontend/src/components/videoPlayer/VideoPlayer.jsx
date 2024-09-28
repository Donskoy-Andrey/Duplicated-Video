// src/components/VideoPlayer.js
import React, { useRef, useState, useEffect, useCallback } from 'react';
import yappyLogo from './yappy.svg';
import './style.css';

const VideoPlayer = ({ src, poster }) => {
    const videoRef = useRef(null); // Ссылка на элемент видео
    const hideControlsTimeout = useRef(null); // Таймер для скрытия контролов

    const [isPlaying, setIsPlaying] = useState(false); // Состояние воспроизведения
    const [showCentralControls, setShowCentralControls] = useState(true); // Отображение центральных контролов

    // отображения контролов
    const showControlsTemporarily = useCallback(() => {
        setShowCentralControls(true);
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current); // Очищаем предыдущий таймер
        }
        //  Новый таймер для скрытия контролов через 1.5 секунды
        hideControlsTimeout.current = setTimeout(() => {
            setShowCentralControls(false);
        }, 1500);
    }, []);

    // Переключение воспроизведения/паузы
    const togglePlayPause = useCallback(() => {
        const video = videoRef.current;
        if (!video) return;
        if (video.paused) {
            video.play(); // Запускаем воспроизведение
            setIsPlaying(true);
        } else {
            video.pause(); // Ставим на паузу
            setIsPlaying(false);
        }
    }, []);

    // Обработчик клика по видео
    const handleVideoClick = () => {
        togglePlayPause(); // Переключаем воспроизведение
        showControlsTemporarily(); // Временно показываем контролы
    };

    // Перемотка назад на 10 секунд
    const rewind10 = useCallback(() => {
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.max(video.currentTime - 10, 0); // Перематываем назад
        showControlsTemporarily(); // Показываем контролы
    }, [showControlsTemporarily]);

    // Перемотка вперед на 10 секунд
    const forward10 = useCallback(() => {
        const video = videoRef.current;
        if (!video) return;
        video.currentTime = Math.min(video.currentTime + 10, video.duration); // Перематываем вперед
        showControlsTemporarily(); // Показываем контролы
    }, [showControlsTemporarily]);

    // Включение/выключение звука
    const toggleMute = useCallback(() => {
        const video = videoRef.current;
        if (!video) return;
        video.muted = !video.muted; // Переключаем состояние звука
    }, []);

    // Переключение полноэкранного режима
    const toggleFullscreen = useCallback(() => {
        const videoContainer = videoRef.current.parentElement;
        if (!document.fullscreenElement) {
            videoContainer.requestFullscreen(); // Входим в полноэкранный режим
        } else {
            document.exitFullscreen(); // Выходим из полноэкранного режима
        }
    }, []);

    // Обработчик нажатия клавиш
    useEffect(() => {
        const handleKeyDown = (e) => {
            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    togglePlayPause(); // Пробел - воспроизведение/пауза
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    forward10(); // Стрелка вправо - перемотка вперед
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    rewind10(); // Стрелка влево - перемотка назад
                    break;
                case 'm':
                case 'M':
                    toggleMute(); // 'M' - выключение/включение звука
                    break;
                default:
                    break;
            }
        };
        window.addEventListener('keydown', handleKeyDown); // Добавляем обработчик события

        return () => {
            window.removeEventListener('keydown', handleKeyDown); // Очищаем обработчик при размонтировании
        };
    }, [togglePlayPause, forward10, rewind10, toggleFullscreen, toggleMute]); // Зависимости эффекта

    // Обработчики событий мыши
    const handleMouseEnter = () => {
        showControlsTemporarily(); // Показываем контролы при наведении
    };

    const handleMouseLeave = () => {
        if (hideControlsTimeout.current) {
            clearTimeout(hideControlsTimeout.current); // Очищаем таймер
        }
        setShowCentralControls(false); // Скрываем контролы
    };

    return (
        <div
            className={`video-container vertical-video ${
                showCentralControls ? 'show-controls' : ''
            }`}
            onClick={handleVideoClick} // Обработчик клика по контейнеру
            onMouseEnter={handleMouseEnter} // Обработчик наведения мыши
            onMouseLeave={handleMouseLeave} // Обработчик ухода мыши
            onMouseMove={showControlsTemporarily} // Обработчик движения мыши
        >
            <video ref={videoRef} src={src} poster={poster} className="video" /> {/* Элемент видео */}

            {/* Заголовок видео */}
            <div className="video-header" onClick={(e) => e.stopPropagation()}>
                <span>AAA IT для</span>
                <img src={yappyLogo} alt="Yappy" className="header-logo" /> {/* Логотип */}
            </div>

            {/* Центральные контролы */}
            <div className="central-controls">
                <button
                    onClick={togglePlayPause}
                    className="central-button play-pause-button"
                    aria-label={isPlaying ? 'Пауза' : 'Воспроизведение'}
                >
                    {isPlaying ? (
                        <i className="fa-solid fa-pause"></i> // Иконка паузы
                    ) : (
                        <i className="fa-solid fa-play"></i> // Иконка воспроизведения
                    )}
                </button>
            </div>
        </div>
    );
};

export default VideoPlayer;
