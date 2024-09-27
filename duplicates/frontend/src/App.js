import './App.css';
import React, { useState } from 'react';
import Header from './components/headers/Header';
import MainPage from './components/main/MainPage';
import InfoPage from './components/info/InfoPage';
import {Footer} from "./components/footer/Footer";
import './index.css'

const App = () => {
  // State to manage the current page
  const [currentPage, setCurrentPage] = useState('main');

  // Render the current page based on the state
  const renderPage = () => {
    switch (currentPage) {
      case 'main':
        return <MainPage />;
      case 'info':
        return <InfoPage />;
      default:
        return <MainPage />;
    }
  };

  return (
      <div className="App">
        <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
        {renderPage()}
        <Footer />
      </div>
  );
};

export default App;