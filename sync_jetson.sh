#!/bin/bash

while true; do
    rsync -avzhe ssh edhitha@192.168.1.28:/home/edhitha/Pictures /Users/aahil/Downloads/edhithaGCS/src/assets/DispImages
    sleep 0.5
done
