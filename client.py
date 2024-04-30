import cv2
import socket
import pickle
import struct
import time

HOST = '201.0.0.1'
PORT = 7000
server_addr = (HOST, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture('video.avi')
frame_count = 0
while cap.isOpened():
    frame_count +=1
    print("frame count:",frame_count)
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    height, width = frame.shape[:2]
    height = (int)(height/2)
    width = (int)(width/2)
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    # send the frame
    # send the frame len first
    frame_data = pickle.dumps(frame)
    s.sendto(struct.pack("Q", len(frame_data)), server_addr)
    packet_size = 1000
    if len(frame_data) > packet_size :
        i = 0
        while i < len(frame_data) - packet_size :
            s.sendto(frame_data[i:i+packet_size], server_addr)
            i += packet_size
            # wait server receive it
            time.sleep(0.001)
        s.sendto(frame_data[i:len(frame_data)], server_addr)
        break
cap.release()
cv2.destroyAllWindows()

