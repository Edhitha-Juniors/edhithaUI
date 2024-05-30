#!/bin/bash

# Function to clean up and terminate the server
cleanup() {
    echo "Terminating C++ server..."
    # Terminate the C++ server process
    pkill -P $$
    exit
}

# Register the cleanup function to handle SIGINT
trap cleanup SIGINT

# Navigate to the directory containing the C++ server code
cd /home/aahil/edhithaGCS/Backend/Manual

# Compile the C++ server
g++ main.cpp -o server -lpistache -lglog `pkg-config --cflags --libs opencv4`

# Run the C++ server
./server
