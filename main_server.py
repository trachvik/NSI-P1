import serial
import serial.tools.list_ports
import time

BAUD = 115200
RPI_VID = 0x2E8A
measure_period = 25000
keep_alive_interval = 15

last_keepalive = time.time()

# I'm using .strip() to avoid unreliable end-of-line characters in the serial communication

def find_rpi_port():
    for port in serial.tools.list_ports.comports():
        if port.vid == RPI_VID: # vid = vendor ID
            print(f'Found Raspberry Pi on {port.device}')
            return port.device
    return None

def connect_rpi():
    global ser
    PORT = find_rpi_port()
    if PORT is None:
        raise RuntimeError('Raspberry Pi not found. Check USB connection.')
    ser = serial.Serial(PORT, BAUD, timeout=1)
    time.sleep(2)  # Wait for Pico to boot


def handshake():
    global last_keepalive
    while True:
        try:
            connect_rpi()
            ser.write(b'<PING>\n')
            response = ser.readline()
            last_keepalive = time.time()
            #print(f'Server received: {response}')
            if response.strip() == b'<PONG:PICO_OK>':
                print('Server: Handshake successful')
                # Set measurement period
                ser.write((f'<SET_T:{measure_period}>\n').encode()) # .encode() converts the string to bytes for serial communication
                last_keepalive = time.time()
                break
        except:
            print('Server: Handshake failed, retrying in 5 seconds...')
            time.sleep(5)
            pass

def leds_control(temp):
    #blue:
    if temp <= 18.0:
        ser.write(b'<LED:0,0,255>\n')
        #print('Server: Blue')
    #azure:
    elif temp > 18.0 and temp <= 22.0:
        ser.write(b'<LED:0,255,255>\n')
        #print('Server: Azure')
    #green:
    elif temp > 22.0 and temp <= 25.0:
        ser.write(b'<LED:0,255,0>\n')
        #print('Server: Green')
    #yellow:
    elif temp > 25.0 and temp <= 28.0:
        ser.write(b'<LED:128,255,0>\n')
        #print('Server: Yellow')
    #red:
    elif temp > 28.0:
        ser.write(b'<LED:255,0,0>\n')
        #print('Server: Red')

handshake()

while True:
    try:
        response = ser.readline()
        #if response:
            #print(f'Raw: {response}')
        if response.startswith(b'<DATA:'):
            last_keepalive = time.time()
            temp = float(response.decode().strip()[6:-1])
            print(f'Received data from RPI: {temp} °C')
            leds_control(temp)
    except Exception as e:
        print(f'Serial error: {e}')
        handshake()  # Try to re-establish connection

    if time.time() - last_keepalive > keep_alive_interval:
        ser.write(b'<KEEP_ALIVE>\n')
        last_keepalive = time.time()
        #print('Server: Sent KEEP_ALIVE to RPI')



