import serial
import serial.tools.list_ports
import time

BAUD = 115200
RPI_VID = 0x2E8A
measure_period = 2000

# I'm using .strip() to avoid unreliable end-of-line characters in the serial communication

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
time.sleep(2)  # Wait for Pico to boot

def handshake():
    ser.write(b'<PING>\n')
    while True:
        response = ser.readline()
        #print(f'Server received: {response}')
        if response.strip() == b'<PONG:PICO_OK>':
            print('Server: Handshake successful')
            break
def measurements_loop():
    while True:
        response = ser.readline()
        #if response:
            #print(f'Raw: {response}')
        if response.startswith(b'<DATA:'):
            temp = float(response.decode().strip()[6:-1])
            print(f'Received data from RPI: {temp} °C')
            leds_control(temp)
def leds_control(temp):
    #blue:
    if temp < 18.0:
        ser.write(b'<LED:0,0,255>\n')
        #print('Server: Blue')
    #azure:
    elif temp > 18.0 and temp < 22.0:
        ser.write(b'<LED:0,255,255>\n')
        #print('Server: Azure')
    #green:
    elif temp > 22.0 and temp < 25.0:
        ser.write(b'<LED:0,255,0>\n')
        #print('Server: Green')
    #yellow:
    elif temp > 25.0 and temp < 28.0:
        ser.write(b'<LED:128,255,0>\n')
        #print('Server: Yellow')
    #red:
    elif temp > 28.0:
        ser.write(b'<LED:255,0,0>\n')
        #print('Server: Red')

handshake()

# Set measurement period to 1000 ms (1 second):
ser.write((f'<SET_T:{measure_period}>\n').encode()) # .encode() converts the string to bytes for serial communication

measurements_loop()
