#!/bin/bash

while true; do
    rsync -azhe ssh edhitha@192.168.1.16:/home/edhitha/virtenv/captured_images/ /Users/aahil/Edhitha/edhithaGCS/Data/Test/images
    sleep 1
done
