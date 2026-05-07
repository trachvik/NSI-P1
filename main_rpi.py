import sys

def handshake():
    while True:
        data = sys.stdin.readline()
        if data == '<PING>\n':
            sys.stdout.write('<PONG:PICO_OK>\n')
            print('RPI:Handshake successful')
            break

handshake()