import sys
import dht
import machine
import uselect

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

sensor = dht.DHT22(machine.Pin(20))

timer_data = machine.Timer()
timer_disconnected = machine.Timer()
timer_blinks = machine.Timer()
timer_connected = machine.Timer()
timer_watchdog = machine.Timer()
blink_counter = 0


flag = False
watchdog_triggered = False
watchdog_period = 20000

state_led = machine.Pin('LED', machine.Pin.OUT)  # Onboard LED

led_r = machine.PWM(machine.Pin(16))
led_r.freq(5000)
led_g = machine.PWM(machine.Pin(17))
led_g.freq(5000)
led_b = machine.PWM(machine.Pin(18))
led_b.freq(5000)

def leds_off():
    led_r.duty_u16(0)
    led_g.duty_u16(0)
    led_b.duty_u16(0)

def handshake():
    while True:
        data = sys.stdin.readline()
        if data.strip() == '<PING>':
            timer_watchdog.init(period=watchdog_period, mode=machine.Timer.ONE_SHOT, callback=watchdog_clb)
            sys.stdout.write('<PONG:PICO_OK>\n') # sys.stdout.write() receives a string and sends UTF-8 encoded bytes to the serial port
            print('RPI:Handshake successful')
            timer_disconnected.deinit()  # stop disconnect blinking when connected
            break

def watchdog_clb(t):
    global watchdog_triggered
    watchdog_triggered = True


def blink_clb(t):
    global blink_counter
    blink_counter += 1
    if blink_counter <= 3:
        state_led.value(1)
        timer_blinks.init(period=100, mode=machine.Timer.ONE_SHOT, callback=blink_off_clb)
    else:
        blink_counter = 0

def blink_off_clb(t):
    state_led.value(0)
    timer_blinks.init(period=100, mode=machine.Timer.ONE_SHOT, callback=blink_clb)

def disconnected_clb(t):
    global blink_counter
    blink_counter = 0
    blink_clb(t)

def data_led_off(t):
    state_led.value(0)


def measure_flag(t):
    global flag
    flag = True

def parse_n_handle(data):
    global init
    if data.startswith('<SET_T:'):
        init = False
        state_led.value(0)
        measure_period = int(data.strip()[7:-1])  # Extract the number from the command | [7:-1] removes the '<SET_T:' prefix (7) and the '>' suffix ()
        timer_watchdog.init(period=watchdog_period, mode=machine.Timer.ONE_SHOT, callback=watchdog_clb)
        timer_data.init(period=measure_period, mode=machine.Timer.PERIODIC, callback=measure_flag)
        

    elif data.startswith('<LED:'):
        timer_watchdog.init(period=watchdog_period, mode=machine.Timer.ONE_SHOT, callback=watchdog_clb)
        #print(f'RPI: Received command to set LED color: {data.strip()}')
        color_values = data.strip()[5:-1].split(',')  # Extract the RGB values from the command | [5:-1] removes the '<LED:' prefix (5) and the '>' suffix ()
        r, g, b = map(int, color_values)  # Convert the RGB values to integers
        led_r.duty_u16(int(r * 65535 / 255))  # Scale 0-255 to 0-65535 for PWM duty cycle
        led_g.duty_u16(int(g * 65535 / 255))
        led_b.duty_u16(int(b * 65535 / 255))


timer_disconnected.init(period=5000, mode=machine.Timer.PERIODIC, callback=disconnected_clb)

handshake()

while True:
    if watchdog_triggered:
        watchdog_triggered = False
        leds_off()
        timer_data.deinit()
        timer_disconnected.init(period=5000, mode=machine.Timer.PERIODIC, callback=disconnected_clb)
        handshake()
    if poll.poll(1):  # 1 ms timeout
        data = sys.stdin.readline()
        if data != '':
            parse_n_handle(data)
    if flag:
        sensor.measure()
        temp = sensor.temperature()
        sys.stdout.write(f'<DATA:{temp:.1f}>\n')
        #print(f'RPI: Sent data to server: {temp:.1f} °C')
        state_led.value(1)
        timer_connected.init(period=50, mode=machine.Timer.ONE_SHOT, callback=data_led_off)
        flag = False
