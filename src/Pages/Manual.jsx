import React, { useState, useEffect, useCallback } from 'react';
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
        coordinates: ''
    });
    const [isLive, setIsLive] = useState(true);
    const [intervalId, setIntervalId] = useState(null);

    const fetchImageUrls = useCallback(async () => {
        try {
            const response = await fetch('http://127.0.0.1:9080/all-images');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const formattedUrls = data.imageUrls.map(url => `http://127.0.0.1:9080/images/${url}`);
            setImageUrls(formattedUrls);
            if (formattedUrls.length > 0 && isLive && !selectedImageUrl) {
                setSelectedImageUrl(formattedUrls[formattedUrls.length - 1]);
            }
        } catch (error) {
            console.error('Error fetching image URLs:', error.message);
        }
    }, [isLive, selectedImageUrl]);

    useEffect(() => {
        if (isLive) {
            fetchImageUrls(); // Fetch images immediately when going live
            const id = setInterval(fetchImageUrls, 2000); // Poll every 2 seconds
            setIntervalId(id);
            return () => clearInterval(id); // Clean up on component unmount or when not live
        } else {
            if (intervalId) {
                clearInterval(intervalId); // Clear interval when not live
                setIntervalId(null); // Reset intervalId to null
            }
        }
    }, [isLive, fetchImageUrls]);

    const handleImageClick = (url) => {
        setSelectedImageUrl(url);
        setIsLive(false); // Prevent automatic updates to the main image
    };

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

    const handleLiveButtonClick = () => {
        setIsLive(true);
        setSelectedImageUrl(''); // Reset to live updates
    };

    const openImage = (event) => {
        if (event.shiftKey && selectedImageUrl) {
            const modal = document.getElementById('image-modal');
            const modalImg = document.getElementById('modal-image');
            if (modal && modalImg) {
                modal.style.display = 'block';
                modalImg.src = selectedImageUrl;
                modalImg.style.maxWidth = '1100px';
                modalImg.style.maxHeight = '700px';
            }
        }
    };

    const closeModal = () => {
        const modal = document.getElementById('image-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    };

    const cropImage = async (x, y) => {
        try {
            const response = await fetch('http://127.0.0.1:9080/crop-image', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ imageUrl: selectedImageUrl.split('/').pop(), x, y})
            });
            if (response.ok) {
                const data = await response.json();
                setCroppedImageUrl(data.croppedImageUrl);
            } else {
                console.error('Failed to crop image');
            }
        } catch (error) {
            console.error('Error cropping image:', error);
        }
    };
     

    const cropClick = (event) => {
        const modalImg = document.getElementById('modal-image');
        if (!modalImg) return;
        
        const rect = modalImg.getBoundingClientRect();
        
        // Adjust coordinates based on the image's scale
        const x = Math.floor((event.clientX - rect.left) / (rect.width / modalImg.naturalWidth));
        const y = Math.floor((event.clientY - rect.top) / (rect.height / modalImg.naturalHeight));
        
        cropImage(x, y);
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
                                        onClick={() => handleImageClick(url)}
                                        className={selectedImageUrl === url ? 'selected' : ''}
                                    />
                                ))}
                            </div>
                            <div className="liveButtonContainer">
                                <button 
                                    className="liveButton"
                                    onClick={handleLiveButtonClick}
                                >
                                    Live
                                </button>
                            </div>
                        </div>
                        <div className="mainImage">
                            {selectedImageUrl && (
                                <img
                                    src={selectedImageUrl}
                                    alt="Main Image"
                                    onClick={openImage}
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
                                <button className="saveButton">Store</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div id="image-modal" className="image-modal" onClick={closeModal}>
                <span className="close-modal" onClick={closeModal}>&times;</span>
                <img
                    id="modal-image"
                    src={selectedImageUrl}
                    alt="Enlarged Image"
                    className="modal-content"
                    onClick={(e) => {
                        e.stopPropagation();
                        cropClick(e);
                    }}
                />
            </div>
        </div>
    );
};

export default Manual;
