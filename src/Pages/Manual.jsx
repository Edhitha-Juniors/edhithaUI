import React, { useState, useEffect } from 'react';
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

    const [imageUrls, setImageUrls] = useState([]); // State to store all image URLs
    const [currentImageUrlIndex, setCurrentImageUrlIndex] = useState(-1); // State to track the index of the current image being displayed

    const handleToggleConnection = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/toggle-connection', {
                method: 'POST'
            });
            if (response.ok) {
                setIsConnected(!isConnected);
            } else {
                console.error('Failed to toggle connection');
            }
        } catch (error) {
            console.error('Error toggling connection:', error);
        }
    };

    const handleToggleGeotag = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/toggle-geotag', {
                method: 'POST'
            });
            if (response.ok) {
                setIsGeotagging(!isGeotagging);
            } else {
                console.error('Failed to toggle geotag');
            }
        } catch (error) {
            console.error('Error toggling geotag:', error);
        }
    };

    const handleLockServo = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/lock-servo', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to lock servo');
            }
        } catch (error) {
            console.error('Error locking servo:', error);
        }
    };

    const handleMissionStart = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/mission-start', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to start mission');
            }
        } catch (error) {
            console.error('Error starting mission:', error);
        }
    };

    const handleArmDrone = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/arm-drone', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to arm drone');
            }
        } catch (error) {
            console.error('Error arming drone:', error);
        }
    };

    const handleDisarmDrone = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/disarm-drone', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to disarm drone');
            }
        } catch (error) {
            console.error('Error disarming drone:', error);
        }
    };

    const handleGuided = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/guided', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to set guided mode');
            }
        } catch (error) {
            console.error('Error setting guided mode:', error);
        }
    };

    const handleAuto = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/auto', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to set auto mode');
            }
        } catch (error) {
            console.error('Error setting auto mode:', error);
        }
    };

    const handleRTL = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/rtl', {
                method: 'POST'
            });
            if (!response.ok) {
                console.error('Failed to set return-to-launch mode');
            }
        } catch (error) {
            console.error('Error setting return-to-launch mode:', error);
        }
    };

    useEffect(() => {
        const interval = setInterval(() => {
            fetchImageUrls();
        }, 2000); // Poll every 2 seconds

        // Cleanup interval on component unmount
        return () => clearInterval(interval);
    }, []);

    const fetchImageUrls = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/all-images');
            if (response.ok) {
                const data = await response.json();
                const formattedUrls = data.imageUrls.map(url => `http://127.0.0.1:9080/images/${url}`);
                setImageUrls(formattedUrls);
                if (formattedUrls.length > 0) {
                    setCurrentImageUrlIndex(formattedUrls.length - 1); // Display the last image
                }
            } else {
                console.error('Failed to fetch image URLs');
            }
        } catch (error) {
            console.error('Error fetching image URLs:', error);
        }
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
                            {imageUrls.length > 0 && <img src={imageUrls[currentImageUrlIndex]} alt="Main Image" />}
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
                            <button className="Control-Button" onClick={handleLockServo}>Lock Servo</button>
                            <button className="Control-Button">Back</button>
                            <button className="Control-Button" onClick={handleMissionStart}>Mission Start</button>
                            <button className="Control-Button" onClick={handleArmDrone}>Arm Drone</button>
                            <button className="Control-Button" onClick={handleDisarmDrone}>Disarm Drone</button>
                            <button className="Control-Button" onClick={handleGuided}>Guided</button>
                            <button className="Control-Button" onClick={handleAuto}>Auto</button>
                            <button className="Control-Button" onClick={handleRTL}>RTL</button>
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
