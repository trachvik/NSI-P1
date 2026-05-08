import sys
import dht
import machine
import uselect

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

sensor = dht.DHT22(machine.Pin(20))
timer = machine.Timer()
flag = False
init = True

def measure_flag(timer):
    global flag
    flag = True

def handshake():
    while True:
        data = sys.stdin.readline()
        if data.strip() == '<PING>':
            sys.stdout.write('<PONG:PICO_OK>\n') # sys.stdout.write() receives a string and sends UTF-8 encoded bytes to the serial port
            print('RPI:Handshake successful')
            break

def parse_n_handle(data):
    global init
    if data.startswith('<SET_T:'):
        init = False
        #print(f'RPI: Received command to set measurement period: {data.strip()} ms')
        measure_period = int(data.strip()[7:-1])  # Extract the number from the command | [7:-1] removes the '<SET_T:' prefix (7) and the '>' suffix ()
        timer.init(period=measure_period, mode=machine.Timer.PERIODIC, callback=measure_flag)

handshake()

while True:
    if poll.poll(0):  # non-blocking
        data = sys.stdin.readline()
        if data != '':
            parse_n_handle(data)
    if flag:
        sensor.measure()
        temp = sensor.temperature()
        sys.stdout.write(f'<DATA:{temp:.1f}>\n')
        print(f'RPI: Sent data to server: {temp:.1f} °C')
        flag = False