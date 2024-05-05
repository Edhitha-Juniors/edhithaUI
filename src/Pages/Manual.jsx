import React, { useState } from 'react';
import '../assets/CSS/Manual.css';
import droneConnectedIcon from '../assets/images/droneConnected.svg';
import logo from '../assets/images/logo.png';

const Manual = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [isGeotagging, setIsGeotagging] = useState(false);
    const [backendData, setBackendData] = useState({
        voltage: '',
        current: '',
        temperature: '',
        message1: 'NO MESSAGE',
        message2: 'Distance from Target - NA'
    });

    const handleToggleConnection = () => {
        setIsConnected(!isConnected);
    };

    const handleToggleGeotag = () => {
        setIsGeotagging(!isGeotagging);
    };



    return (
        <div className="manual-container">
            <div className="header-container">
                <header className="header">
                    <img src={logo} alt="Logo" className="logoM" />
                    <h1>Manual Flight</h1>
                    <button className={`connection-button ${isConnected ? 'green' : ''}`} onClick={handleToggleConnection}>
                        <img src={droneConnectedIcon} alt="Drone Connection" />
                        <span className="connect-text">Connect</span>
                    </button>
                </header>
            </div>
            <div className="content-container">
                <div className="left-container">
                    <div className="image-box">
                        <div className="mainImage">
                            <p>Main Image</p>
                            {/* Content for main image */}
                        </div>
                        <div className="croppedImage">
                            <p>Cropped Image</p>
                            {/* Content for cropped image */}
                        </div>
                    </div>


                    <div className="inputsContainer">
                        <input type="text" placeholder="Shape" />
                        <input type="text" placeholder="Colour" />
                        <input type="text" placeholder="Alphanumeric" />
                        <input type="text" placeholder="Alphanumeric Colour" />
                        <input type="text" placeholder="Coordinates (to be rendered)" value={backendData.coordinates} readOnly />
                        <button className="saveButton">Store</button>
                    </div>
                </div>

                <div className="right-container">
                    <div className="top-right-container">
                        <div className="button-grid">
                            <button
                                className={`Control-Button ${isGeotagging ? 'red' : ''} ${isGeotagging ? 'Geotag_Button' : ''}`}
                                onClick={handleToggleGeotag}
                            >
                                {isGeotagging ? 'Stop Geotag' : 'Start Geotag'}
                            </button>
                            <button className="Control-Button">Lock Servo</button>
                            <button className="Control-Button">Back</button>
                            <button className="Control-Button">Mission Start</button>
                            <button className="Control-Button">Arm Drone</button>
                            <button className="Control-Button">Disarm Drone</button>
                            <button className="Control-Button">Guided</button>
                            <button className="Control-Button">Auto</button>
                            <button className="Control-Button">RTL</button>
                        </div>
                    </div>
                    <div className="bottom-right-container">
                        <div className="bottom-up-container">
                            <div className="data-box">
                                <input type="text" placeholder="Voltage" value={backendData.voltage} readOnly />
                            </div>
                            <div className="data-box">
                                <input type="text" placeholder="Current" value={backendData.current} readOnly />
                            </div>
                            <div className="data-box">
                                <input type="text" placeholder="Temperature" value={backendData.temperature} readOnly />
                            </div>
                        </div>
                        <div className="bottom-down-container">
                            <div className="message-box">
                                <p>{backendData.message1}</p>
                            </div>
                            <div className="message-box">
                                <p>{backendData.message2}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Manual;
