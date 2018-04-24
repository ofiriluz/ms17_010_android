__version__ = 1.0

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from iplist import IPList
from kivy.logger import Logger
from subnet_scanner import SubnetScanner
import socket
import sys


class ScannerLayout(GridLayout):
    def __init__(self, **kwargs):
        Logger.fatal("Init the scanner layout")
        my_ip = self.__get_ip()
        if not my_ip:
            Logger.fatal('Cannot init scanner, failed to find IP, aborting')
            sys.exit(1)
        self.scanner = SubnetScanner(my_ip, start_sub=self.on_scan_started, update_sub=self.on_scan_update, finish_sub=self.on_scan_finished)
        self.ip_list = IPList(size_hint_y=0.8)
        self.scan_button = Button(text="Scan", size_hint_y=0.2)
        self.scan_button.bind(on_press=self.on_scan_button_cb)
        kwargs['cols'] = 1
        kwargs['size_hint'] = (1.0, 1.0)

        super(ScannerLayout, self).__init__(**kwargs)

        self.add_widget(self.scan_button)
        self.add_widget(self.ip_list)

    def __get_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            Logger.info('My IP = ' + ip)
            s.close()
            return ip
        except Exception, e:
            Logger.fatal(str(e))
        return None

    def on_scan_button_cb(self, instance):
        Logger.fatal("Starting the scanner")
        self.scanner.start_scan()
        self.scan_button.disabled = True

    def on_scan_started(self):
        Logger.info('Scanner Start CB')

    def on_scan_finished(self):
        Logger.info('Scanner Finish CB')
        self.scan_button.disabled = False

    def on_scan_update(self):
        Logger.info('Scanner Update CB')
        self.ip_list.set_ips([t['IP'] for t in self.scanner.get_scanned_targets()])


class MainApp(App):
    def build(self):
        layout = ScannerLayout()
        return layout


if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception, e:
        Logger.fatal(e.message)
        Logger.fatal(str(e))
        popup = Popup(title='ERROR', content=Label(text=str(e)),auto_dismiss=False)
        popup.open()
