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

    // Fetches images constantly
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

    // Shift+Click: Open modal with selected image
    const openImage = (event) => {
        if (event.shiftKey && selectedImageUrl) {
            const modal = document.getElementById('image-modal');
            const modalImg = document.getElementById('modal-image');
            if (modal && modalImg) {
                modal.style.display = 'block';
                modalImg.src = selectedImageUrl;
                modalImg.style.maxWidth = '1100px'; // Adjust max width as needed
                modalImg.style.maxHeight = '700px'; // Adjust max height as needed
            }
        }
    };

    // Close modal
    const closeModal = () => {
        const modal = document.getElementById('image-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    };

    const cropClick = async (event) => {
        const modalImg = document.getElementById('modal-image');
        if (modalImg) {
            const rect = modalImg.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const coordinates = `${x},${y}`; // Example format; adjust as per backend requirements

            // Send coordinates and selected image URL to backend
            try {
                const response = await fetch('http://127.0.0.1:9080/crop-image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ imageUrl: selectedImageUrl, coordinates }),
                });
                if (response.ok) {
                    const data = await response.json();
                    setCroppedImageUrl(data.croppedImageUrl); // Update cropped image URL if needed
                    setBackendData((prevData) => ({ ...prevData, coordinates })); // Update coordinates in backendData
                } else {
                    console.error('Failed to crop image on the backend');
                }
            } catch (error) {
                console.error('Error cropping image:', error);
            }
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
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            {/* Modal for displaying selected image */}
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
