from gpiozero import Button
from gpiozero import DigitalInputDevice

in_sensor_proximity = Button(17)
in_sensor_flow = DigitalInputDevice(19)
in_limit_opened = Button(27)
in_limit_closed = Button(22)

def proximityDown():
    print("proximity is down")

def proximityUp():
    print("proximity is up")

def flowDown():
    print("flow is down")

def flowUp():
    print("flow is up")

def openDown():
    print("open is down")

def openUp():
    print("open is up")

def closeDown():
    print("close is down")

def closeUp():
    print("close is up")


in_limit_closed.when_activated = closeUp
in_limit_closed.when_deactivated = closeDown
in_limit_opened.when_activated = openUp
in_limit_opened.when_deactivated = openDown
in_sensor_flow.when_activated = flowUp
in_sensor_flow.when_deactivated = flowDown
in_sensor_proximity.when_activated = proximityUp
in_sensor_proximity.when_deactivated = proximityDown

while True :
    pass