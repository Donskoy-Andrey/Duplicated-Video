import React from 'react';
import "./style.css"
import hacks_ai from "../../img/hacks_ai.png"

const Header = ({ currentPage, setCurrentPage }) => {
    return (
        <nav className="navbar navbar-expand-md bg-body-tertiary ">
            <div className="container-fluid">
                <button
                    className="navbar-toggler ml-auto"
                    data-bs-toggle="collapse"
                    data-bs-target="#navbarSupportedContent"
                    aria-controls="navbarSupportedContent"
                    aria-expanded="false"
                    type="button"
                    // onClick={() => document.getElementById("navbarSupportedContent").classList.toggle("show")}
                >
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarSupportedContent">
                    <ul className="navbar-nav  me-auto mb-2 mb-lg-0">
                        <li className={`nav-item ${currentPage === 'main' ? 'active' : ''}`}>
                            <button className="nav-link btn btn-link fs" onClick={() => setCurrentPage('main')}>
                                Главная
                            </button>
                        </li>

                        <li className={`nav-item ${currentPage === 'zip' ? 'active' : ''}`}>
                            <button className="nav-link btn btn-link" onClick={() => setCurrentPage('zip')}>
                                Загрузка архива
                            </button>
                        </li>
                        <li className={`nav-item ${currentPage === 'info' ? 'active' : ''}`}>
                            <button className="nav-link btn btn-link" onClick={() => setCurrentPage('info')}>
                                Команда
                            </button>
                        </li>
                    </ul>
                </div>
            </div>
            <img src={hacks_ai} height="30px" alt="Logo" className="navbar-img"/>
        </nav>
    );
};

export default Header;