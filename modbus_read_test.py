import minimalmodbus
import time

BAUDRATE = 9600
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_NONE
MODE = minimalmodbus.MODE_RTU
OLD_ADDRESS = 12
NEW_ADDRESS : int = 1

device = minimalmodbus.Instrument('COM4', NEW_ADDRESS)
device.serial.baudrate = BAUDRATE
device.serial.bytesize = BYTESIZES
device.serial.parity = PARITY
device.serial.stopbits = STOPBITS
device.serial.timeout = 0.5
device.mode = MODE
device.clear_buffers_before_each_transaction = True

device3 = minimalmodbus.Instrument('COM4', 3)
device3.serial.baudrate = BAUDRATE
device3.serial.bytesize = BYTESIZES
device3.serial.parity = PARITY
device3.serial.stopbits = STOPBITS
device3.serial.timeout = 0.5
device3.mode = MODE
device3.clear_buffers_before_each_transaction = True

while True:
    try:
        data = device.read_register(5,1,3,False)
        time.sleep(.1)
        data3 = device3.read_register(0x0101,0,3,False)
        # print('data 1 :',data)
        # print('data 3', data3)
        print('data 1 :',data, 'data 3', data3)
        time.sleep(1)
    except Exception as e:
        print(e)