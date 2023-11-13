import numpy as np
import kivy
import sys
import os
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.config import Config
from kivy.metrics import dp
from datetime import datetime
from pathlib import Path
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from gpiozero import Button
from gpiozero import RotaryEncoder
from gpiozero import DigitalInputDevice
from gpiozero import Motor
from gpiozero import DigitalOutputDevice
from gpiozero import PWMOutputDevice
import minimalmodbus
import time
import qrcode
import requests

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

colors = {
    "Blue": {
        "200": "#A3D8DD",
        "500": "#A3D8DD",
        "700": "#A3D8DD",
    },

    "BlueGray": {
        "200": "#09343C",
        "500": "#09343C",
        "700": "#09343C",
    },

    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#EEEEEE",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },

    "Dark": {
        "StatusBar": "101010",
        "AppBar": "#E0E0E0",
        "Background": "#111111",
        "CardsDialogs": "#000000",
        "FlatButtonDown": "#333333",
    },
}

MAINTENANCE= True
DEBUG = True

SERVER = 'https://app.kickyourplast.com/api/'
MACHINE_CODE = 'KYP001'

if (DEBUG) :
    try :
        r = requests.patch(SERVER + 'machines/' + MACHINE_CODE, data={
            'stock' : str(levelMainTank)+'%',
            'status' : 'not_ready'            
        })
    except Exception as e:
        print(e)

# modbus rtu communication paramater setup
BAUDRATE = 9600
BYTESIZES = 8
STOPBITS = 1
TIMEOUT = 0.5
PARITY = minimalmodbus.serial.PARITY_NONE
MODE = minimalmodbus.MODE_RTU

if(not DEBUG):
    # input declaration 
    in_sensor_proximity = Button(17)
    in_sensor_flow = DigitalInputDevice(19)
    in_limit_opened = Button(27)
    in_limit_closed = Button(22)

    # modbus communication of sensor declaration 
    mainTank = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
    mainTank.serial.baudrate = BAUDRATE
    mainTank.serial.bytesize = BYTESIZES
    mainTank.serial.parity = PARITY
    mainTank.serial.stopbits = STOPBITS
    mainTank.serial.timeout = 0.5
    mainTank.mode = MODE
    mainTank.clear_buffers_before_each_transaction = True

    coldTank = minimalmodbus.Instrument('/dev/ttyUSB0', 2)
    coldTank.serial.baudrate = BAUDRATE
    coldTank.serial.bytesize = BYTESIZES
    coldTank.serial.parity = PARITY
    coldTank.serial.stopbits = STOPBITS
    coldTank.serial.timeout = 0.5
    coldTank.mode = MODE
    coldTank.clear_buffers_before_each_transaction = True

    normalTank = minimalmodbus.Instrument('/dev/ttyUSB0', 3)
    normalTank.serial.baudrate = BAUDRATE
    normalTank.serial.bytesize = BYTESIZES
    normalTank.serial.parity = PARITY
    normalTank.serial.stopbits = STOPBITS
    normalTank.serial.timeout = 0.5
    normalTank.mode = MODE
    normalTank.clear_buffers_before_each_transaction = True

    # output declaration 
    out_valve_cold = DigitalOutputDevice(20)
    out_valve_normal = DigitalOutputDevice(26)
    out_pump_main = DigitalOutputDevice(21)
    out_pump_cold = DigitalOutputDevice(5)
    out_pump_normal = DigitalOutputDevice(6)
    out_stepper_enable = DigitalOutputDevice(23)
    out_stepper_direction = DigitalOutputDevice(24)
    out_stepper_pulse = PWMOutputDevice(12)
    out_motor_linear = Motor(16, 9)

    out_valve_cold.off()
    out_valve_normal.off()
    out_pump_main.on()
    out_pump_normal.off()
    out_pump_normal.off()
    out_motor_linear.stop()

valve_cold = False
valve_normal = False
pump_main = False
pump_cold = False
pump_normal = False
linear_motor = False
stepper_open = False

pulsePerLiter = 450
pulsePerMiliLiter = 450/1000

cold = False
product = 0
idProduct = 0
productPrice = 0
pulse = 0
levelMainTank = 0
levelNormalTank = 0
levelColdTank = 0
maxMainTank = 1500
maxNormalTank = 500
maxColdTank = 500
qrSource = 'qr_payment.png'

def countPulse():
    global pulse
    pulse +=1

if (not DEBUG) : in_sensor_flow.when_activated = countPulse 

def stepperAct(exec : str):
    global out_stepper_enable, out_stepper_direction ,out_stepper_pulse, in_limit_opened, in_limit_closed
    
    if(not DEBUG):
        out_stepper_enable.on()
    
    if (exec == 'open'):
        if(not DEBUG):
            out_stepper_direction.on()
            while not in_limit_opened.value:
                out_stepper_pulse.value = 0.5
            
            out_stepper_pulse.value = 0
    else:
        if(not DEBUG):
            out_stepper_direction.off()
            while not in_limit_closed.value:
                out_stepper_pulse.value = 0.5
            
            out_stepper_pulse.value = 0

class ScreenSplash(MDBoxLayout):
    screen_manager = ObjectProperty(None)
    app_window = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ScreenSplash, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .01)
        Clock.schedule_interval(self.regular_check, 1)

    def update_progress_bar(self, *args):
        if (self.ids.progress_bar.value + 1) < 100:
            raw_value = self.ids.progress_bar_label.text.split('[')[-1]
            value = raw_value[:-2]
            value = eval(value.strip())
            new_value = value + 1
            self.ids.progress_bar.value = new_value
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(new_value)
        else:
            self.ids.progress_bar.value = 100
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(100)
            time.sleep(0.5)
            self.screen_manager.current = 'screen_choose_product'
            return False

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank, maxColdTank, maxMainTank, maxNormalTank, out_pump_main, out_valve_cold, out_valve_normal

        # program for reading sensor end control system algorithm
        if(not DEBUG):
            try:
                read = mainTank.read_register(5,0,3,False)
                levelMainTank = read * 100 / maxMainTank
                time.sleep(.1)
                read = coldTank.read_register(0x0101,0,3,False)
                levelColdTank = read * 100 / maxColdTank
                time.sleep(.1)
                read = normalTank.read_register(0x0101,0,3,False)
                levelNormalTank = read * 100 / maxNormalTank    
                
            except Exception as e:
                print(e)
        
        # Tank mechanism
        if (not MAINTENANCE):
            if (levelMainTank <= 40):
                if (not DEBUG) :
                    try :
                        r = requests.patch(SERVER + 'machines/' + MACHINE_CODE, data={
                            'stock' : str(levelMainTank)+'%',
                            'status' : 'not_ready'
                        })
                    except Exception as e:
                        print(e)
                    print('sending request to server')
            else:
                try :
                    r = requests.patch(SERVER + 'machines/' + MACHINE_CODE, data={
                        'stock' : str(levelMainTank)+'%',
                        'status' : 'ready'
                    })
                except Exception as e:                    
                    print(e)
                    
            if (levelColdTank <=40):
                if (not DEBUG) : 
                    out_valve_cold.on()
                    out_pump_main.off()
            
            if (levelNormalTank <=40):
                if (not DEBUG) : 
                    out_valve_normal.on()
                    out_pump_main.off()

            if (levelColdTank >= 85):
                if (not DEBUG) : 
                    out_valve_cold.off()
                    out_pump_main.on()

            if (levelNormalTank >= 85):
                if (not DEBUG) : 
                    out_valve_normal.off()
                    out_pump_main.off()

        # scan kupon QR CODE
        # if (something):
        #     try :
        #         r = requests.post(SERVER + 'transactions/' + KODE_KUPON + '/used_machine', data={
        #             'machine_code' : MACHINE_CODE
        #         })

        #         toast(r.json().message)
        #     except Exception as e:
        #         print(e)

class ScreenChooseProduct(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChooseProduct, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, .1)
        
        try :
            r = requests.get(SERVER + 'products', {all : True})
            print(r.json()['data'])
            self.products = r.json()['data']
        except Exception as e:
            print(e)

    def cold_mode(self, value):
        global cold
        cold = value

    def choose_payment(self, size, id, price):
        global product, idProduct, productPrice
        self.screen_manager.current = 'screen_choose_payment'
        product = size
        idProduct = id
        productPrice = price
        print(idProduct,type(idProduct))
        print(product,type(product))
        print(productPrice,type(productPrice))

    def screen_info(self):
        self.screen_manager.current = 'screen_info'

    def regular_check(self, *args):
        # program for displaying IO condition
        if (cold):
            self.ids.bt_cold.md_bg_color = "#3C9999"
            self.ids.bt_normal.md_bg_color = "#09343C"
        else:
            self.ids.bt_cold.md_bg_color = "#09343C"
            self.ids.bt_normal.md_bg_color = "#3C9999"       

class ScreenChoosePayment(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenChoosePayment, self).__init__(**kwargs)

    def pay(self, method):
        global qr, qrSource, product, idProduct, cold, productPrice

        print(method)
        try:
            if(method=="GOPAY"):
                # ..... create transaction
                qrSource = self.create_transaction(
                    machine_code=MACHINE_CODE,
                    method='gopay',
                    product_id=idProduct,
                    product_size=product,
                    qty=1,
                    price=productPrice,
                    product_type="cold" if (cold) else "normal",
                    # phone=self.phone
                )

                f = open('qr_payment.png', 'wb')
                f.write(requests.get(qrSource).content)
                f.close

                self.screen_manager.current = 'screen_qr_payment'
                print("payment qris")

                # .... scheduling payment check
                # Clock.schedule_interval(self.payment_check, 1)
                toast("successfully pay with GOPAY")

            elif(method=="QRIS"):
                # ..... create transaction
                qrSource = self.create_transaction(
                    machine_code=MACHINE_CODE,
                    method='qris',
                    product_id=idProduct,
                    product_size=product,
                    qty=1,
                    price=productPrice,
                    product_type="cold" if (cold) else "normal",
                    # phone=self.phone
                )
                
                time.sleep(0.1)
                qr.add_data(qrSource)
                qr.make(fit=True)

                img = qr.make_image(back_color=(255, 255, 255), fill_color=(55, 95, 100))
                img.save("qr_payment.png")

                self.screen_manager.current = 'screen_qr_payment'
                print("payment qris")

                # .... scheduling payment check
                # Clock.schedule_interval(self.payment_check, 1)
                toast("successfully pay with QRIS")
        except:
            print("payment error")

    def create_transaction(self, method, machine_code, product_id, product_size, qty, price, product_type, phone='-'):
        try :
            r = requests.post(SERVER + 'machine_transactions', json={
                "payment_method": method,
                "machine_code": machine_code,
                "phone": phone,
                "items": [
                    {
                        "product_id": product_id,
                        "qty": qty,
                        "size": product_size,
                        "unit_price": price,
                        "drink_type": product_type
                    }
                ]
            })
            # print(r.json()['data'])
            return r.json()['data']['payment_response_parameter']['qr_string'] if (method == 'qris') else r.json()['data']['payment_response_parameter']['actions'][0]['url']
        except Exception as e:
            print(e)
    
    def payment_check(self):
        try :
            r = requests.get(SERVER + 'machine_transactions/' + self.transaction_id)
            
            if (r.json()['data']['payment_status'] == 'success'):
                toast('payment success')
                self.screen_manager.current = 'screen_operate'
                Clock.unschedule(self.payment_check)

            elif (r.json()['data']['payment_status'] != 'pending'):
                toast("payment failed")
                self.screen_manager.current = 'screen_choose_product'
                Clock.unschedule(self.payment_check)
                
        except Exception as e:
            print(e)

    def screen_choose_product(self):
        self.screen_manager.current = 'screen_choose_product'

class ScreenOperate(MDBoxLayout):
    screen_manager = ObjectProperty(None)
    fill = False

    def __init__(self, **kwargs):       
        super(ScreenOperate, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, .1)

    def move_up(self):
        global out_motor_linear
        if (not DEBUG) : out_motor_linear.forward()
        print("move up")
        toast("moving tumbler base up")

    def move_down(self):
        global out_motor_linear
        if (not DEBUG) : out_motor_linear.backward()
        print("move down")
        toast("moving tumbler base down")

    def fill_start(self):
        global pulse
        if (not DEBUG and not self.fill) :
            pulse = 0 
            self.fill = True

        print("fill start")
        toast("water filling is started")

    def fill_stop(self):
        global out_pump_cold, out_pump_normal
        if(not DEBUG):
            out_pump_cold.off()
            out_pump_normal.off()
            self.fill = False

        print("fill stop")
        toast("thank you for decreasing plastic bottle trash by buying our product")
        self.screen_manager.current = 'screen_choose_product'

    def regular_check(self, *args):
        global pulse, product, pulsePerMiliLiter, in_limit_closed, in_limit_opened, in_sensor_proximity, out_pump_cold, out_pump_normal, stepperAct

        if (self.fill):
            if (pulse <= pulsePerMiliLiter*product):
                if (in_sensor_proximity):
                    if (not in_limit_opened) : stepperAct('open')
                    out_pump_cold.on() if (cold) else out_pump_normal.on()
                else :
                    out_pump_cold.off()
                    out_pump_normal.off()
                    toast("please put your tumbler")

            else :
                out_pump_cold.off()
                out_pump_normal.off()
                stepperAct('close')
                self.fill = False
                toast("thank you for decreasing plastic bottle trash by buying our product")

class ScreenQRPayment(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenQRPayment, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, 1)
        
    def regular_check(self, *args):
        self.ids.image_qr_payment.source = 'qr_payment.png'
        self.ids.image_qr_payment.reload()
        pass

    def cancel(self):
        self.screen_manager.current = 'screen_choose_product'

    def dummy_success(self):
        self.screen_manager.current = 'screen_operate' 

class ScreenInfo(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenInfo, self).__init__(**kwargs)

    def screen_choose_product(self):
        self.screen_manager.current = 'screen_choose_product'

    def screen_maintenance(self):
        self.screen_manager.current = 'screen_maintenance'      
 

class ScreenMaintenance(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenMaintenance, self).__init__(**kwargs)
        Clock.schedule_interval(self.regular_check, .1)

    def act_valve_cold(self):
        global valve_cold, out_valve_cold
        if (valve_cold):
            valve_cold = False 
            if (not DEBUG) : out_valve_cold.off()
        else:
            valve_cold = True 
            if (not DEBUG) : out_valve_cold.on()

    def act_valve_normal(self):
        global valve_normal, out_valve_normal
        if (valve_normal):
            valve_normal = False 
            if (not DEBUG) : out_valve_normal.off()
        else:
            valve_normal = True 
            if (not DEBUG) : out_valve_normal.on()

    def act_pump_main(self):
        global pump_main, out_pump_main
        if (pump_main):
            pump_main = False            
            if (not DEBUG) : out_pump_main.on()
        else:
            pump_main = True
            if (not DEBUG) : out_pump_main.off()

    def act_pump_cold(self):
        global pump_cold, out_pump_cold
        if (pump_cold):
            pump_cold = False
            if (not DEBUG) : out_pump_cold.off()
        else:
            pump_cold = True 
            if (not DEBUG) : out_pump_cold.on()

    def act_pump_normal(self):
        global pump_normal, out_pump_normal
        if (pump_normal):
            pump_normal = False
            if (not DEBUG) : out_pump_normal.off()
        else:
            pump_normal = True
            if (not DEBUG) : out_pump_normal.on()

    def act_open(self):
        global stepper_open, in_limit_opened

        # stepper_open is boolean, if stepper_open on it can change GPIO condition to move open or close
        # if (stepper_open):
        #     stepperAct('open')
        #     stepper_open = False
        # else:
        #     stepperAct('close')
        #     stepper_open = True
        # if not lsOpen
        if (not DEBUG) : 
            if (not in_limit_opened) :
                stepperAct('open')

        stepper_open = True
        

    def act_close(self):
        global stepper_open, in_limit_closed

        # stepper_open is boolean, if stepper_open on it can change GPIO condition to move open or close
        # if (stepper_open):
        #     stepperAct('open')
        #     stepper_open = False
        # else:
        #     stepperAct('close')
        #     stepper_open = True

        if (not DEBUG) : 
            if (not in_limit_closed) :
                stepperAct('close')
                
        stepper_open = False

    def act_up(self):
        global linear_motor, out_motor_linear
        self.ids.bt_up.md_bg_color = "#3C9999"
        if (not DEBUG) : out_motor_linear.forward()
        toast("tumbler base is going up")

        # linear_motor is boolean, if linear motor on it can change GPIO condition to move up or down
        # if (linear_motor):
        #     pass

    def act_down(self):
        global linear_motor, out_motor_linear
        self.ids.bt_down.md_bg_color = "#3C9999"
        if (not DEBUG) : out_motor_linear.backward()
        toast("tumbler base is going down")

        # if (linear_motor):
        #     pass

    def act_stop(self):
        global linear_motor, out_motor_linear
        self.ids.bt_up.md_bg_color = "#09343C"
        self.ids.bt_down.md_bg_color = "#09343C"
        if (not DEBUG) : out_motor_linear.stop()

    def exit(self):
        self.screen_manager.current = 'screen_choose_product'

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank

        self.ids.lb_level_main.text = str(levelMainTank) + '%'
        self.ids.lb_level_cold.text = str(levelColdTank) + '%'
        self.ids.lb_level_normal.text = str(levelNormalTank) + '%'

        # program for displaying IO condition        
        if (valve_cold):
            self.ids.bt_valve_cold.md_bg_color = "#3C9999"
        else:
            self.ids.bt_valve_cold.md_bg_color = "#09343C"

        if (valve_normal):
            self.ids.bt_valve_normal.md_bg_color = "#3C9999"
        else:
            self.ids.bt_valve_normal.md_bg_color = "#09343C"

        if (pump_main):
            self.ids.bt_pump_main.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_main.md_bg_color = "#09343C"

        if (pump_cold):
            self.ids.bt_pump_cold.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_cold.md_bg_color = "#09343C"

        if (pump_normal):
            self.ids.bt_pump_normal.md_bg_color = "#3C9999"
        else:
            self.ids.bt_pump_normal.md_bg_color = "#09343C"

        if (stepper_open):
            self.ids.bt_open.md_bg_color = "#3C9999"
            self.ids.bt_close.md_bg_color = "#09343C"
        else:
            self.ids.bt_open.md_bg_color = "#09343C"
            self.ids.bt_close.md_bg_color = "#3C9999"

class WaterDispenserMachineApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.accent_palette = "Blue"
        self.icon = 'asset/Icon_Logo.png'
        Window.fullscreen = 'auto'
        Window.borderless = True
        # Window.size = 1080, 640
        # Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    WaterDispenserMachineApp().run()