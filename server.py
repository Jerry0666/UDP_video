import cv2
import socket
import pickle
import struct
import threading

def showFrame(frame):
    cv2.imshow('Server', frame)
    print("show frame:")
    if cv2.waitKey(1000 *30) == 13:
        return

HOST = '201.0.0.1'
PORT = 7000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

payload_size = struct.calcsize("Q")
frame_count = 0
dropIncompletePacket = True
while dropIncompletePacket == False:
    data = b""
    frame_count += 1
    print("frame count:", frame_count)
    while len(data) < payload_size:
        packet,_ = s.recvfrom(4 * 1024)  
        print("packet len: ", len(packet))
        if not packet:
            break
        data += packet
    if not data:
        break
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    print("msg_size:", msg_size)
    while len(data) < msg_size:
        recvData,_ = s.recvfrom(60000)  
        data += recvData
        print("data len: ", len(data))
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    t = threading.Thread(target = showFrame, args=(frame,))
    t.start()
  
data = b""
msg_size = 0  
drop = False 
while dropIncompletePacket:
    packet,_ = s.recvfrom(60000)
    if len(packet) == 8:
        # initial the frame
        print("packet len: ", len(packet))
        data = b""
        frame_count += 1
        print("frame count:", frame_count)
        msg_size = struct.unpack("Q", packet)[0]
        print("msg_size: ", msg_size)
        drop = False
    elif len(packet) == 1000:
        if drop:
            continue
        data += packet
        print("data len:", len(data))
    elif len(packet) + len(data) == msg_size:
        if drop:
            continue
        data += packet
        frame_data = data[:msg_size]
        data = data[msg_size:]
        frame = pickle.loads(frame_data)
        t = threading.Thread(target = showFrame, args=(frame,))
        t.start()
        break
    else :
        print("drop")
        drop = True
        
while dropIncompletePacket == False:
    if dropIncompletePacket == True:
        break
    
cv2.destroyAllWindows()