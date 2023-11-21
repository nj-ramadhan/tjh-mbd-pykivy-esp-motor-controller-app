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
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.ticker import AutoMinorLocator
from kivy.properties import ObjectProperty
import time

plt.style.use('bmh')

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

colors = {
    "Blue": {
        "200": "#1c74bb",
        "500": "#1c74bb",
        "700": "#1c74bb",
    },

    "Orange": {
        "200": "#f08421",
        "500": "#f08421",
        "700": "#f08421",
    },

    "Gray": {
        "200": "#bbbbbb",
        "500": "#bbbbbb",
        "700": "#bbbbbb",
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
            self.screen_manager.current = 'screen_main_menu'
            return False

    def regular_check(self, *args):
        global levelColdTank, levelMainTank, levelNormalTank, maxColdTank, maxMainTank, maxNormalTank, out_pump_main, out_valve_cold, out_valve_normal

class ScreenMainMenu(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenMainMenu, self).__init__(**kwargs)

    def nav_datalog_history(self):
        self.screen_manager.current = 'screen_datalog_history'

    def nav_amp_chart(self):
        self.screen_manager.current = 'screen_amp_chart'

    def nav_main_menu(self):
        self.screen_manager.current = 'screen_main_menu'

    def nav_info(self):
        self.screen_manager.current = 'screen_info'      

class ScreenDatalogHistory(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenDatalogHistory, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init)
        # Clock.schedule_interval(self.regular_check, 1)

    def regular_check(self, dt):
        pass

    def delayed_init(self, dt):
        layout = self.ids.layout_tables
        
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=4,
            column_data=[
                ("No.", dp(10)),
                ("Avg. Volt [V]", dp(27)),
                ("Avg. Curr [A]", dp(27)),
                ("Unbal. Volt [%]", dp(27)),
                ("Unbal. Curr [%]", dp(27)),
            ],
        )
        layout.add_widget(self.data_tables)

    def reset_data(self):
        global data_base
        global dt_measure
        global dt_current
        global dt_voltage
        
        data_base = np.zeros([5, 1])
        dt_measure = np.zeros(6)
        dt_current = np.zeros(10)
        dt_voltage = np.zeros(10)
        
        layout = self.ids.layout_tables
        
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=4,
            column_data=[
                ("No.", dp(10)),
                ("Volt [V]", dp(27)),
                ("Curr [mA]", dp(27)),
                ("Resi [kOhm]", dp(27)),
                ("Std Dev Res", dp(27)),
                ("IP (R decay)", dp(27)),
            ],
        )
        layout.add_widget(self.data_tables)

    def save_data(self):
        try:

            now = datetime.now().strftime("/%d_%m_%Y_%H_%M_%S.dat")
            # disk = str(DISK_ADDRESS) + now
            disk = os.getcwd() + now
            head="%s \n%.2f \n%s \n%s \n0 \n1" % (now, dt_distance, mode, len(data_base.T[2]))
            foot="0 \n0 \n0 \n0 \n0"
            with open(disk,"wb") as f:
                np.savetxt(f, data_write.T, fmt="%.3f", delimiter="\t", header=head, footer=foot, comments="")
            print("sucessfully save data")
            toast("sucessfully save data")
        except:
            print("error saving data")
            toast("error saving data")
    
    def nav_datalog_history(self):
        self.screen_manager.current = 'screen_datalog_history'

    def nav_amp_chart(self):
        self.screen_manager.current = 'screen_amp_chart'

    def nav_main_menu(self):
        self.screen_manager.current = 'screen_main_menu'

    def nav_info(self):
        self.screen_manager.current = 'screen_info' 

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
                self.screen_manager.current = 'screen_main_menu'
                Clock.unschedule(self.payment_check)
                
        except Exception as e:
            print(e)

    def screen_main_menu(self):
        self.screen_manager.current = 'screen_main_menu'

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
        self.screen_manager.current = 'screen_main_menu'

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
        self.screen_manager.current = 'screen_main_menu'

    def dummy_success(self):
        self.screen_manager.current = 'screen_operate' 

class ScreenInfo(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenInfo, self).__init__(**kwargs)

    def screen_main_menu(self):
        self.screen_manager.current = 'screen_main_menu'

    def screen_maintenance(self):
        self.screen_manager.current = 'screen_maintenance'      
 

class ScreenMaintenance(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenMaintenance, self).__init__(**kwargs)

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
        self.screen_manager.current = 'screen_main_menu'


class ScreenAmpChart(MDBoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenAmpChart, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init)
        # Clock.schedule_interval(self.regular_check, 2)

    def regular_check(self, dt):
        try:
            self.a
            self.theta
            self.data
            self.show_data
            self.show_theta
            
            self.fig = plt.figure()
            self.ax = self.fig.add_subplot(111, polar=True)
            self.ax.set_theta_offset(np.pi / 2)
            self.ax.set_theta_direction(-1)
            self.ax.set_rmax(200)
            self.ax.set_xticklabels([
                r'$day 1$',
                r'$day 2$',
                r'$day 3$',
                r'$day 4$',
                r'$day 5$',
                r'$day 6$',
                r'$day 7$',
                r'$day 8$',
                ])
            self.ax.grid(True)
            self.ax.set_title("Amp Chart", va='bottom')
            self.ax.plot(self.theta, self.data, color='r', linewidth=2)

            self.a = self.a + 1
            # self.fig.set_facecolor("#eeeeee")
            # self.fig.tight_layout()
            
            # self.ax.set_xlabel("distance [m]", fontsize=10)
            # self.ax.set_ylabel("n", fontsize=10)
            # self.ax.set_facecolor("#eeeeee")

            # # datum location
            # max_data = np.max(data_base[2,:data_limit])
            # cmap, norm = mcolors.from_levels_and_colors([0.0, max_data, max_data * 2],['green','red'])
            # self.ax.scatter(visualized_data_pos[0,:data_limit], -visualized_data_pos[1,:data_limit], c=data_base[2,:data_limit], cmap=cmap, norm=norm, label=l_electrode[0], marker='o')
            # electrode location
            self.ids.layout_amp_chart.clear_widgets()
            self.ids.layout_amp_chart.add_widget(FigureCanvasKivyAgg(self.fig))

            print("successfully show graphic")
        
        except:
            print("error show graphic")


    def delayed_init(self, dt):
        try:
            self.n = 115
            self.a = 0
            self.data = np.random.uniform(100.0, 200.0, self.n)
            self.angle = np.arange(0, self.n, 1)
            self.theta = np.pi * np.deg2rad(self.angle)

            # self.show_theta = np.array([])
            # self.show_data = np.array([])

            self.fig, self.ax = plt.subplots(polar=True)

            # self.fig = plt.figure()
            # self.ax = self.fig.add_subplot(111, polar=True)
            self.ax.set_theta_offset(np.pi / 2)
            self.ax.set_theta_direction(-1)
            self.ax.set_rmax(200)
            self.ax.set_xticklabels([
                r'$day 1$',
                r'$day 2$',
                r'$day 3$',
                r'$day 4$',
                r'$day 5$',
                r'$day 6$',
                r'$day 7$',
                r'$day 8$',
                ])
            # self.ax.grid(True)
            self.ax.set_title("Amp Chart", va='bottom')
            self.ax.plot(self.theta, self.data, color='r', linewidth=2)

            # self.fig, self.ax = plt.subplots()
            # self.fig.set_facecolor("#eeeeee")
            # self.fig.tight_layout()
            # l, b, w, h = self.ax.get_position().bounds
            # self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
            
            # self.ax.set_xlabel("distance [m]", fontsize=10)
            # self.ax.set_ylabel("n", fontsize=10)

            self.ids.layout_amp_chart.add_widget(FigureCanvasKivyAgg(self.fig))    

        except:
            print("error show graph")

    # def delayed_init(self, dt):
    #     self.fig, self.ax = plt.subplots()
    #     self.fig.set_facecolor("#eeeeee")
    #     self.fig.tight_layout()
    #     l, b, w, h = self.ax.get_position().bounds
    #     self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
        
    #     self.ax.set_xlabel("distance [m]", fontsize=10)
    #     self.ax.set_ylabel("n", fontsize=10)

    #     self.ids.layout_amp_chart.add_widget(FigureCanvasKivyAgg(self.fig))        

    def measure(self):
        global flag_run
        if(flag_run):
            flag_run = False
        else:
            flag_run = True

    def reset_graph(self):
        global data_base
        global data_pos

        data_base = np.zeros([5, 1])
        data_pos = np.zeros([2, 1])

        try:
            self.ids.layout_graph.clear_widgets()
            self.fig, self.ax = plt.subplots()
            self.fig.set_facecolor("#eeeeee")
            self.fig.tight_layout()
            l, b, w, h = self.ax.get_position().bounds
            self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
            
            self.ax.set_xlabel("distance [m]", fontsize=10)
            self.ax.set_ylabel("n", fontsize=10)

            self.ids.layout_graph.add_widget(FigureCanvasKivyAgg(self.fig))        
            print("successfully reset graphic")
        
        except:
            print("error reset graphic")


    def save_graph(self):
        try:
            now = datetime.now().strftime("/%d_%m_%Y_%H_%M_%S.jpg")
            disk = str(DISK_ADDRESS) + now
            self.fig.savefig(disk)
            print("sucessfully save graph")
            toast("sucessfully save graph")
        except:
            print("error saving graph")
            toast("error saving graph")
                
    def autosave_graph(self):
        try:
            now = datetime.now().strftime("/%d_%m_%Y_%H_%M_%S.jpg")
            cwd = os.getcwd()
            disk = cwd + now
            self.fig.savefig(disk)
            print("sucessfully auto save graph")
            # toast("sucessfully save graph")
        except:
            print("error auto saving graph")
            # toast("error saving graph")
    
    def nav_datalog_history(self):
        self.screen_manager.current = 'screen_datalog_history'

    def nav_amp_chart(self):
        self.screen_manager.current = 'screen_amp_chart'

    def nav_main_menu(self):
        self.screen_manager.current = 'screen_main_menu'

    def nav_info(self):
        self.screen_manager.current = 'screen_info' 

class ESPMotorControllerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Gray"
        self.icon = 'asset/Icon_Logo.png'
        # Window.fullscreen = 'auto'
        # Window.borderless = True
        Window.size = 1366, 768
        Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')
        return screen
   


if __name__ == '__main__':
    ESPMotorControllerApp().run()