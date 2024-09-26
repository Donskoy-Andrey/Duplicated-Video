import React from 'react';
import ali from "../../img/ali.png"
import artmed from "../../img/artmed.png"
import donskow from "../../img/donskow.png"
import ivan from "../../img/ivan.png"
import tmn from "../../img/tmn.png"

const InfoPage = () => {
    let we = {
        "andrey": {
            "name": "Андрей Донской",
            "picture": donskow,
            "job": "DS Газпромнефть",
            "education": ["Академия Аналитиков Авито, 2024", "Университет Сириус"],
            "mail": "donskoi.ae@gmail.com",
            "position": 'ML',
            "tg": "https://t.me/doncheg",
            "github": "https://github.com/Donskoy-Andrey"
        },
        "ali": {
            "name": "Али Рамазанов",
            "picture": ali,
            "job": "Стартап Skyrus",
            "education": ["Tinkoff Education, 2023", "Университет Сириус"],
            "mail": "artiebears@mail.ru",
            "position": 'Backend',
            "tg": "https://t.me/AliRamazanovN",
            "github": "https://github.com/AliRn9"
        },
        "artem": {
            "name": "Артем Медведев",
            "picture": artmed,
            "job": "Стартап Skyrus",
            "education": ["VK Education, 2023", "Университет Сириус"],
            "mail": "artiebears@mail.ru",
            "position": 'Frontend',
            "tg": "https://t.me/artiebears13",
            "github": "https://github.com/artiebears13"
        },
        "ivan": {
            "name": "Иван Бутаков",
            "picture": ivan,
            "job": "ИВМ РАН",
            "education": ["ШАД, 2023", "МФТИ,Университет Сириус"],
            "mail": "vanessbut@yandex.ru",
            "position": 'ML',
            "tg": "https://t.me/emptyhooks",
            "github": "https://github.com/Donskoy-Andrey"
        },
        "timofey": {
            "name": "Тимофей Щудро",
            "picture": tmn,
            "job": "Стартап Skyrus",
            "education": ["Университет Сириус"],
            "mail": "artiebears@mail.ru",
            "position": 'DevOps',
            "tg": "https://t.me/TeeMan508",
            "github": "https://github.com/Donskoy-Andrey"
        },
    };

    return (
        <div className="main-page">
            <div className="container mt-4 mx-auto">
                <h1 className="text-center mb-5">Информация о команде</h1>
                <div className="row ml-0">
                    {Object.entries(we).map(([key, bro]) => (
                        <div key={key} className="col-sm mb-4 mx-auto">
                            <div className="card animated-card">
                                <img src={bro.picture} alt="img"/>
                                <div className="card-body">
                                    <div className="card-badge">{bro.position}</div>
                                    <h5 className="card-title">{bro.name}</h5>
                                    <hr />
                                    <p className="card-text"><i className="fa-solid fa-suitcase description-icon"></i>{bro.job}</p>
                                    {bro.education.map((educ, name) => (
                                        <p className="card-text"><i
                                            className="fa-solid fa-book description-icon"></i>{educ}</p>
                                    ))}
                                    <a href={`mailto:${bro.mail}`} className="btn btn-primary btn-card__bottom">Написать</a>
                                    <div className="icons">
                                        <a href={bro.tg}><i
                                            className="fa-brands fa-telegram fa-lg tg-icon"></i></a>
                                        <a href={bro.github}><i
                                            className="fa-brands fa-github fa-lg tg-icon"></i></a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default InfoPage;
