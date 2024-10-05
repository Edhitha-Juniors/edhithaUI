#!/bin/bash

while true; do
    rsync -avzhe ssh edhitha@192.168.1.21:/home/code25/camcap/images/ /Users/aahil/Downloads/edhithaGCS/Data/images/
    sleep 1
done
