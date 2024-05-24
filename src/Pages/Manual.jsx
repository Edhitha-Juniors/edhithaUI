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
    const [selectedImageUrl, setSelectedImageUrl] = useState(''); // State to store the selected image URL
    const [clickPosition, setClickPosition] = useState({ x: 0, y: 0 }); // State to store click position for cropping

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
                    setSelectedImageUrl(formattedUrls[formattedUrls.length - 1]); // Display the last image by default
                }
            } else {
                console.error('Failed to fetch image URLs');
            }
        } catch (error) {
            console.error('Error fetching image URLs:', error);
        }
    };

    const handleImageClick = (e) => {
        if (e.shiftKey && selectedImageUrl) {
            const windowWidth = 1100;
            const windowHeight = 700;

            const imageWindow = window.open("", "ImageWindow", `width=${windowWidth},height=${windowHeight}`);
            imageWindow.document.write(`<img src="${selectedImageUrl}" style="width:auto; height:auto; max-width:100%; max-height:100%;">`);
        }
    };

    const handleImageCrop = async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/crop-image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    imageUrl: selectedImageUrl.split('/').pop(),
                    clickX: clickPosition.x,
                    clickY: clickPosition.y
                })
            });
            if (response.ok) {
                console.log('Cropped image saved successfully');
                // You can handle success here, like showing a notification
            } else {
                console.error('Failed to save cropped image');
            }
        } catch (error) {
            console.error('Error saving cropped image:', error);
        }
    };

    const handleImageMouseDown = (e) => {
        setClickPosition({ x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY });
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
                                    onMouseDown={handleImageMouseDown}
                                />
                            )}
                        </div>
                        <div className="croppedImage">
                            <div className="croppedImageDisplay">
                                {/* Add your cropped image here */}
                                <img src="your_image_url" alt="Cropped Image" />
                            </div>
                            {/* Content for cropped image */}
                            <div className="inputsContainer">
                                <input className="inputBox" type="text" placeholder="Shape" />
                                <input className="inputBox" type="text" placeholder="Colour" />
                                <input className="inputBox" type="text" placeholder="Alphanumeric" />
                                <input className="inputBox" type="text" placeholder="Alphanumeric Colour" />
                                <input type="text" placeholder="Coordinates (to be rendered)" className="coordinatesBox" value={backendData.coordinates} readOnly />
                                <button className="saveButton" onClick={handleImageCrop}>Store</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Manual;
