raspistill --nopreview -w 128 -h 160 -q 5 -o /tmp/pic.jpg -tl 100 -t 9999999 -th 0:0:0 &

export LD_LIBRARY_PATH=/home/pi/src/mjpg-streamer-code-182/mjpg-streamer
cd ./mjpg-streamer-code-182/mjpg-streamer

./mjpg_streamer -i "input_file.so -f /tmp/ -n pic.jpg" -o "output_http.so -w ./www"
