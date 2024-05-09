import React, { useState, useEffect } from 'react';
import '../assets/CSS/Manual.css';
import droneConnectedIcon from '../assets/images/droneConnected.svg';
import logo from '../assets/images/logo.png';

const Manual = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [isGeotagging, setIsGeotagging] = useState(false);
    const [backendImageList, setBackendImageList] = useState([]);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        fetchImageList();
    }, []);

    useEffect(() => {
        if (backendImageList.length > 0) {
            const intervalId = setInterval(() => {
                setCurrentImageIndex(prevIndex => {
                    const nextIndex = (prevIndex + 1) % backendImageList.length;
                    // If next index is 0, indicating the last image, stop cycling
                    if (nextIndex === 0) clearInterval(intervalId);
                    return nextIndex === 0 ? prevIndex : nextIndex;
                });
            }, 1000);

            return () => clearInterval(intervalId);
        }
    }, [backendImageList]);


    const fetchImageList = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8080/imglst');
            if (response.ok) {
                const imageList = await response.json();
                setBackendImageList(imageList);
            } else {
                console.error('Failed to fetch image list');
            }
        } catch (error) {
            console.error('Error fetching image list:', error);
        }
    };

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
                        <span className="connect-text">{isConnected ? 'Connected' : 'Connect'}</span>
                    </button>
                </header>
            </div>
            <div className="content-container">
                <div className="left-container">
                    <div className="image-box">
                        <div className="mainImage">
                            {backendImageList.length > 0 && (
                                <img src={`http://127.0.0.1:8080/img/${backendImageList[currentImageIndex]}`} alt="Main Image" />
                            )}
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
                        <input type="text" placeholder="Coordinates (to be rendered)" readOnly />
                        <button className="saveButton">Store</button>
                    </div>
                </div>
                <div className="right-container">
                    <div className="top-right-container">
                        <div className="button-grid">
                            <button className={`Control-Button ${isGeotagging ? 'red Geotag_Button' : ''}`} onClick={handleToggleGeotag}>
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
                                <input type="text" placeholder="Voltage" readOnly />
                            </div>
                            <div className="data-box">
                                <input type="text" placeholder="Current" readOnly />
                            </div>
                            <div className="data-box">
                                <input type="text" placeholder="Temperature" readOnly />
                            </div>
                        </div>
                        <div className="bottom-down-container">
                            <div className="message-box">
                                <p>NO MESSAGE</p>
                            </div>
                            <div className="message-box">
                                <p>Distance from Target - NA</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Manual;
