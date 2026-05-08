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

led_r = machine.PWM(machine.Pin(16))
led_r.freq(5000)
led_g = machine.PWM(machine.Pin(17))
led_g.freq(5000)
led_b = machine.PWM(machine.Pin(18))
led_b.freq(5000)

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
    elif data.startswith('<LED:'):
        #print(f'RPI: Received command to set LED color: {data.strip()}')
        color_values = data.strip()[5:-1].split(',')  # Extract the RGB values from the command | [5:-1] removes the '<LED:' prefix (5) and the '>' suffix ()
        r, g, b = map(int, color_values)  # Convert the RGB values to integers
        led_r.duty_u16(int(r * 65535 / 255))  # Scale 0-255 to 0-65535 for PWM duty cycle
        led_g.duty_u16(int(g * 65535 / 255))
        led_b.duty_u16(int(b * 65535 / 255))

handshake()

while True:
    if poll.poll(1):  # 1 ms timeout
        data = sys.stdin.readline()
        if data != '':
            parse_n_handle(data)
    if flag:
        sensor.measure()
        temp = sensor.temperature()
        sys.stdout.write(f'<DATA:{temp:.1f}>\n')
        #print(f'RPI: Sent data to server: {temp:.1f} °C')
        flag = False