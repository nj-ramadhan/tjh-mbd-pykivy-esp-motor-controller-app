from gpiozero import DigitalOutputDevice
from gpiozero import PWMOutputDevice
import time

out_stepper_enable = DigitalOutputDevice(23)
out_stepper_direction = DigitalOutputDevice(24)
out_stepper_pulse = PWMOutputDevice(12)

out_stepper_enable.on()
out_stepper_direction.on()
out_stepper_pulse.value = 0.5
time.sleep(2)

out_stepper_pulse.value = 0
time.sleep(2)

out_stepper_direction.off()
out_stepper_pulse.value = 0.5
time.sleep(2)

out_stepper_pulse.value = 0
time.sleep(2)