__version__ = 1.0

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from iplist import IPList
from kivy.logger import Logger
from subnet_scanner import SubnetScanner
from zzz_exploit import exploit
import socket
import sys
import traceback


class ScannerLayout(GridLayout):
    def __init__(self, **kwargs):
        Logger.fatal("Init the scanner layout")
        my_ip = self.__get_ip()
        if not my_ip:
            Logger.fatal('Cannot init scanner, failed to find IP, aborting')
            sys.exit(1)
        self.scanner = SubnetScanner(my_ip,
                                     nthreads=20,
                                     start_sub=self.on_scan_started,
                                     update_sub=self.on_scan_update,
                                     finish_sub=self.on_scan_finished)
        self.ip_list = IPList(size_hint_y=0.7)
        self.scan_button = Button(text="Scan", size_hint_y=0.15)
        self.scan_button.bind(on_press=self.on_scan_button_cb)
        self.attack_button = Button(text='Attack', size_hint_y=0.15)
        self.attack_button.bind(on_press=self.on_attack_button_cb)
        self.attack_button.disabled = True
        kwargs['cols'] = 1
        kwargs['size_hint'] = (1.0, 1.0)

        super(ScannerLayout, self).__init__(**kwargs)

        self.add_widget(self.scan_button)
        self.add_widget(self.attack_button)
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

    def on_attack_button_cb(self, instance):
        selected_ip = str(self.ip_list.list_adapter.selection[0].text).split('-')[0].strip()
        Logger.info('Selected IP to attack = ' + selected_ip)
        if exploit(selected_ip):
            Logger.info("Exploit Succ!")
        else:
            Logger.warn("Exploit Failure")

    def on_scan_button_cb(self, instance):
        Logger.fatal("Starting the scanner")
        self.scanner.start_scan()
        self.scan_button.disabled = True

    def on_scan_started(self):
        Logger.info('Scanner Start CB')

    def on_scan_finished(self):
        Logger.info('Scanner Finish CB')
        if len(self.scanner.get_scanned_targets()) > 0:
            self.attack_button.disabled = False
        self.scan_button.disabled = False

    def on_scan_update(self):
        Logger.info('Scanner Update CB')
        self.ip_list.set_ips([t['IP'] + ' - ' + t['OS'] for t in self.scanner.get_scanned_targets()])


class MainApp(App):
    def build(self):
        layout = ScannerLayout()
        return layout


if __name__ == "__main__":
    try:
        MainApp().run()
    except Exception, e:
        Logger.fatal(e.message)
        traceback.print_exc()
        popup = Popup(title='ERROR', content=Label(text=str(e)),auto_dismiss=False)
        popup.open()
