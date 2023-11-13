import minimalmodbus
import time

BAUDRATE = 9600
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_NONE
MODE = minimalmodbus.MODE_RTU
OLD_ADDRESS = 1
NEW_ADDRESS : int = 3

device = minimalmodbus.Instrument('COM4', NEW_ADDRESS)
device.serial.baudrate = BAUDRATE
device.serial.bytesize = BYTESIZES
device.serial.parity = PARITY
device.serial.stopbits = STOPBITS
device.serial.timeout = 0.5
device.mode = MODE
device.clear_buffers_before_each_transaction = True


while True:
    try:
        data = device.read_register(0x0101,0,3,False)
        print(data)
        time.sleep(1)
    except Exception:
        print(Exception)

# try:
#     device.write_register(0x0200, 2, 0, 16, False)
#     print('success')
# except Exception as e:
#     print(e)