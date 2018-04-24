__version__ = 1.0

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from iplist import IPList
from kivy.logger import Logger


class ControlLayout(GridLayout):
    def on_scan_cb(self, instance):
        Logger.fatal("Inside Callback")
        l = ['127.0.0.' + str(i) for i in range(10)]
        self.ip_list.add_ips(l)

    def __init__(self, **kwargs):
        Logger.fatal("THIS IS THE BEGINNING")
        self.ip_list = IPList(size_hint_y=0.8)
        self.scan_button = Button(text="Scan", size_hint_y=0.2)
        self.scan_button.bind(on_press=self.on_scan_cb)
        kwargs['cols'] = 1
        kwargs['size_hint'] = (1.0, 1.0)

        super(ControlLayout, self).__init__(**kwargs)

        self.add_widget(self.scan_button)
        self.add_widget(self.ip_list)

    def get_ip_widger(self):
        return self.ip_list


class MainApp(App):
    def build(self):
        layout = ControlLayout()
        return layout


if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception, e:
        Logger.fatal(e.message)
        Logger.fatal(str(e))
        popup = Popup(title='ERROR', content=Label(text=str(e)),auto_dismiss=False)
        popup.open()
