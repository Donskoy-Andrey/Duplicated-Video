import React from 'react';


function ExampleModal({isOpen, onClose, onAccept}) {
    // console.log(isOpen);
    if (!isOpen) return null;

    return (
        <div className="modal">
            <div className="modal__content">
                <h2> Примеры запросов</h2>
                <br></br>
                <button className="modal-close" onClick={onClose}>x</button>
                <div className="modal-buttons">
                    <div className="modal-buttons__row">
                        <div className="modal-buttons__col">
                            <p className="modal-buttons__specification">Пример 2</p>
                            <p className="modal-buttons__result">Описание</p>
                        </div>
                        <button className="btn btn-primary modal-buttons__button" onClick={() => onAccept("first")}>
                            Отправить
                        </button>
                    </div>
                    <div className="modal-buttons__row">
                        <div className="modal-buttons__col">
                            <p className="modal-buttons__specification">Пример 1</p>
                            <p className="modal-buttons__result">Описание</p>
                        </div>
                        <button className="btn btn-primary modal-buttons__button"
                                onClick={() => onAccept("second")}>
                            Отправить
                        </button>
                    </div>

                </div>

            </div>
        </div>
    );
}

export default ExampleModal;