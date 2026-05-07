import serial
import serial.tools.list_ports
import time

BAUD = 115200
RPI_VID = 0x2E8A

def find_rpi_port():
    for port in serial.tools.list_ports.comports():
        if port.vid == RPI_VID: # vid = vendor ID
            print(f'Found Raspberry Pi on {port.device}')
            return port.device
    return None

PORT = find_rpi_port()
if PORT is None:
    raise RuntimeError('Raspberry Pi not found. Check USB connection.')

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Wait for the serial connection to initialize

def handshake():
    global ser
    ser.write(b'<PING>\n')
    while True:
        response = ser.readline()
        print(f'Server received: {response}')
        if response == b'<PONG:PICO_OK>\n':
            print('Server:Handshake successful')
            break

handshake()


