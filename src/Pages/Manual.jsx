import React, { useState, useEffect } from 'react';
import '../assets/CSS/Manual.css';
import droneConnectedIcon from '../assets/images/droneConnected.svg';
import logo from '../assets/images/logo.png';

const Manual = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [croppedImageUrl, setCroppedImageUrl] = useState('');
    const [imageUrls, setImageUrls] = useState([]);
    const [selectedImageUrl, setSelectedImageUrl] = useState('');
    const [backendData, setBackendData] = useState({
        voltage: '',
        current: '',
        temperature: '',
        message1: 'NO MESSAGE',
        message2: 'Distance from Target - NA',
        coordinates: '' // Add coordinates property to backendData
    });

    const handleToggleConnection = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/toggle-connection', { method: 'POST' });
            if (response.ok) {
                setIsConnected(!isConnected);
            } else {
                console.error('Failed to toggle connection');
            }
        } catch (error) {
            console.error('Error toggling connection:', error);
        }
    };

    useEffect(() => {
        const interval = setInterval(() => {
            fetchImageUrls();
        }, 2000); // Poll every 2 seconds

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
                    setSelectedImageUrl(formattedUrls[formattedUrls.length - 1]);
                }
            } else {
                console.error('Failed to fetch image URLs');
            }
        } catch (error) {
            console.error('Error fetching image URLs:', error);
        }
    };

    const handleImageClick = async (e) => {
        const clickX = e.nativeEvent.offsetX;
        const clickY = e.nativeEvent.offsetY;
        try {
            const response = await fetch('http://127.0.0.1:9080/crop-image-preview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    imageUrl: selectedImageUrl.split('/').pop(),
                    clickX,
                    clickY
                })
            });
            if (response.ok) {
                const data = await response.json();
                setCroppedImageUrl(`http://127.0.0.1:9080/images/${data.croppedImageUrl}`);
            } else {
                console.error('Failed to preview cropped image');
            }
        } catch (error) {
            console.error('Error previewing cropped image:', error);
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
                <div className="Top-container">
                    <div className="image-box">
                        <div className="image-grid">
                            <div className="grid-container">
                                {imageUrls.map((url, index) => (
                                    <img
                                        key={index}
                                        src={url}
                                        alt={`Grid Image ${index}`}
                                        onClick={() => setSelectedImageUrl(url)}
                                        className={selectedImageUrl === url ? 'selected' : ''}
                                    />
                                ))}
                            </div>
                        </div>
                        <div className="mainImage">
                            {selectedImageUrl && (
                                <img
                                    src={selectedImageUrl}
                                    alt="Main Image"
                                    onClick={handleImageClick}
                                />
                            )}
                        </div>
                        <div className="croppedImage">
                            <div className="croppedImageDisplay">
                                {croppedImageUrl && (
                                    <img src={croppedImageUrl} alt="Cropped Image" />
                                )}
                            </div>
                            <div className="inputsContainer">
                                <input className="inputBox" type="text" placeholder="Shape" />
                                <input className="inputBox" type="text" placeholder="Colour" />
                                <input className="inputBox" type="text" placeholder="Alphanumeric" />
                                <input className="inputBox" type="text" placeholder="Alphanumeric Colour" />
                                <input type="text" placeholder="Coordinates (to be rendered)" className="coordinatesBox" value={backendData.coordinates} readOnly />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Manual;
