# !/bin/bash
while true; do
    rsync -azhve ssh edhitha@192.168.1.21:/home/edhitha/DCIM/test_cam/images /Users/aahil/Edhitha/edhithaGCS/Data/Test/
    sleep 1
done
