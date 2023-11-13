from gpiozero import DigitalOutputDevice
import time

a = DigitalOutputDevice(16)
b = DigitalOutputDevice(25)

a.on()
b.off()
time.sleep(2)
a.off()
time.sleep(2)
b.on()
time.sleep(2)
b.off()

print('ok')