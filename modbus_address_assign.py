import minimalmodbus

BAUDRATE = 19200
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_EVEN
MODE = minimalmodbus.MODE_RTU
OLD_ADDRESS = 12
NEW_ADDRESS : int = 1

device = minimalmodbus.Instrument('dev/ttyUSB0', OLD_ADDRESS)
device.serial.baudrate = BAUDRATE
device.serial.bytesize = BYTESIZES
device.serial.parity = PARITY
device.serial.stopbits = STOPBITS
device.serial.timeout = 0.5
device.mode = MODE
device.clear_buffers_before_each_transaction = True

try:
    device.write_register(2, NEW_ADDRESS, 0, 16, False)
    print('success')
except Exception:
    print(Exception)