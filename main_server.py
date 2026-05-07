import serial
import time
#import threading

PORT = 'COM15'  # TO DO : auto detect port
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

def handshake():
    global ser
    ser.write(b'<PING>\n')
    while True:
        response = ser.readline()
        print(f'Server received: {response}')
        if response == b'<PONG:PICO_OK>\n':
            print('Server:Handshake successful')
            break

time.sleep(2)  # Wait for the serial connection to initialize   
handshake()

#timer = threading.Timer(1.0, handshake)
#timer.start()


