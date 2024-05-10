#!/bin/bash

# Navigate to the directory containing the C++ server code
cd /home/aahil/edhithaGCS/Backend/Manual

# Compile the C++ server
g++ -o server main.cpp -lpistache

# Run the C++ server in the background
./server &
