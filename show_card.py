from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.card import MDCard

KV = '''
<CardProducts>
    padding: 4
    size_hint: None, None
    size: "200dp", "100dp"
    ripple: True

    MDRelativeLayout:

        MDIconButton:
            icon: "dots-vertical"
            pos_hint: {"top": 1, "right": 1}

        MDLabel:
            id: label
            text: root.text
            adaptive_size: True
            color: "grey"
            pos: "12dp", "12dp"
            bold: True


MDScreen:

    MDGridLayout:
        id: box
        cols:2
        adaptive_size: True
        spacing: "56dp"
        pos_hint: {"center_x": .5, "center_y": .5}
'''


class CardProducts(MDCard):
    '''Implements a material design v3 card.'''
    text = StringProperty()

    def choose_payment(self, text):
        print(text)

class Example(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        return Builder.load_string(KV)

    def on_start(self):
        styles = {
            "elevated": "#f6eeee", "filled": "#f4dedc", "outlined": "#f8f5f4"
        }
        for style in styles.keys():
            self.root.ids.box.add_widget(
                CardProducts(
                    line_color=(0.2, 0.2, 0.2, 0.8),
                    style=style,
                    text=style.capitalize(),
                    md_bg_color=styles[style],
                    shadow_offset=(0, -1),
                    # on_press= CardProducts().choose_payment(str(style.capitalize()))
                )
            )
    



Example().run()